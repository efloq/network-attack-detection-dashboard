"""Mevcut Random Forest tabanlı CSV analiz akışı."""

from __future__ import annotations

import html
import io
import logging
import time
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from constants import (
    ATTACK_DESCRIPTIONS,
    ATTACK_NAMES,
    GENERAL_RECOMMENDATIONS,
    MODEL_FILE_NAME,
    RESULT_COLUMNS,
    RISK_COLORS,
    RISK_MAP,
    SECURITY_RECOMMENDATIONS,
)
from helpers import (
    MissingColumnsError,
    current_analysis_time,
    make_file_signature,
)
from ui import render_file_details, section_title

LOGGER = logging.getLogger(__name__)


@st.cache_resource(show_spinner=False)
def load_model(model_path: str) -> Any:
    """Eğitilmiş makine öğrenmesi modelini önbelleğe alarak yükler."""
    return joblib.load(model_path)

def read_csv_file(file_bytes: bytes) -> pd.DataFrame:
    """Yüklenen CSV içeriğini bir DataFrame olarak okur."""
    return pd.read_csv(io.BytesIO(file_bytes))

def prepare_features(dataframe: pd.DataFrame, model: Any) -> pd.DataFrame:
    """Sonuç sütunlarını kaldırır ve model özellik sırasını korur."""
    features = dataframe.drop(
        columns=[
            column
            for column in RESULT_COLUMNS
            if column in dataframe.columns
        ],
        errors="ignore",
    )

    model_feature_names = getattr(model, "feature_names_in_", None)
    if model_feature_names is not None:
        required_columns = list(model_feature_names)
        missing_columns = [
            column
            for column in required_columns
            if column not in features.columns
        ]
        if missing_columns:
            raise MissingColumnsError(missing_columns)
        features = features.loc[:, required_columns]
    else:
        expected_count = getattr(model, "n_features_in_", None)
        if expected_count is not None and features.shape[1] != expected_count:
            raise ValueError(
                "Model "
                f"{expected_count} özellik bekliyor; CSV dosyasında "
                f"{features.shape[1]} özellik bulundu."
            )


    features = features.apply(
        pd.to_numeric,
        errors="coerce",
    )

    features = features.replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    invalid_columns = (
        features.columns[features.isna().any()]
        .astype(str)
        .tolist()
    )

    if invalid_columns:
        shown_columns = ", ".join(invalid_columns[:10])

        extra_count = len(invalid_columns) - 10
        extra_text = (
            f" ve {extra_count} sütun daha"
            if extra_count > 0
            else ""
        )

        raise ValueError(
            "CSV dosyasında boş, sonsuz veya sayısal olmayan değerler bulundu: "
            f"{shown_columns}{extra_text}. "
            "Dosyayı temizleyip yeniden yükleyin."
        )

        

    return features

def prediction_to_label(value: Any) -> str:
    """Model çıktısını okunabilir saldırı sınıfına dönüştürür."""
    if isinstance(value, str) and value in RISK_MAP:
        return value

    try:
        class_id = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Model bilinmeyen bir sınıf değeri üretti: {value}"
        ) from exc

    if class_id not in ATTACK_NAMES:
        raise ValueError(
            f"Model tanımsız bir sınıf numarası üretti: {class_id}"
        )

    return ATTACK_NAMES[class_id]

def run_prediction(
    dataframe: pd.DataFrame,
    model: Any,
) -> pd.DataFrame:
    """Model tahminini çalıştırır ve sonuç tablosunu oluşturur."""
    clean_dataframe = dataframe.drop(
        columns=[
            column
            for column in RESULT_COLUMNS
            if column in dataframe.columns
        ],
        errors="ignore",
    )

    features = prepare_features(clean_dataframe, model)

    prediction = model.predict(features)
    prediction_labels = [
        prediction_to_label(value) for value in prediction
    ]

    result = clean_dataframe.copy()
    result["Tahmin"] = prediction_labels
    result["Risk Seviyesi"] = result["Tahmin"].map(RISK_MAP)

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)

        confidence_scores = probabilities.max(axis=1) * 100
        result["Güven Skoru (%)"] = confidence_scores.round(2)

        if probabilities.shape[1] >= 2:
            sorted_indices = probabilities.argsort(axis=1)
            second_class_indices = sorted_indices[:, -2]

            second_probabilities = (
                probabilities[
                    range(len(probabilities)),
                    second_class_indices,
                ]
                * 100
            )

            model_classes = model.classes_

            second_predictions = [
                prediction_to_label(model_classes[index])
                for index in second_class_indices
            ]

            result["İkinci Olası Sınıf"] = second_predictions
            result["İkinci Olasılık (%)"] = second_probabilities.round(2)

        result["Tahmin Güveni"] = result["Güven Skoru (%)"].apply(
            lambda score: (
                "Yüksek"
                if score >= 90
                else "Orta"
                if score >= 70
                else "Düşük"
            )
        )

    return result
    

def calculate_summary(result: pd.DataFrame) -> dict[str, Any]:
    """CSV raporunda kullanılan temel istatistikleri hesaplar."""
    attack_rows = result[result["Tahmin"] != "Benign"]
    attack_counts = attack_rows["Tahmin"].value_counts()

    most_common_attack = None
    most_common_count = 0
    if not attack_counts.empty:
        most_common_attack = attack_counts.index[0]
        most_common_count = int(attack_counts.iloc[0])

    return {
        "total_records": int(len(result)),
        "detected_type_count": int(result["Tahmin"].nunique()),
        "critical_count": int(
            (result["Risk Seviyesi"] == "Kritik").sum()
        ),
        "attack_count": int(len(attack_rows)),
        "most_common_attack": most_common_attack,
        "most_common_count": most_common_count,
    }

def render_metrics(
        
    summary: dict[str, Any],
    result: pd.DataFrame,
) -> None:
    """CSV genel istatistiklerini metrik kartlarında gösterir."""

    section_title("Genel İstatistikler", "01")

    column_1, column_2, column_3, column_4 = st.columns(4)

    column_1.metric(
        "Toplam Kayıt",
        summary["total_records"],
    )

    column_2.metric(
        "Tespit Edilen Tür Sayısı",
        summary["detected_type_count"],
    )

    column_3.metric(
        "Kritik Risk Sayısı",
        summary["critical_count"],
    )

    if "Güven Skoru (%)" in result.columns:
        average_confidence = result["Güven Skoru (%)"].mean()

        column_4.metric(
            "Ortalama Güven",
            f"%{average_confidence:.2f}",
        )
    else:
        column_4.metric(
            "Ortalama Güven",
            "-",
        )

def render_most_common_attack(summary: dict[str, Any]) -> None:
    """Benign hariç en sık tespit edilen saldırıyı gösterir."""
    section_title("En Sık Tespit Edilen Saldırı", "02")

    if summary["most_common_attack"] is None:
        message = "Herhangi bir saldırı tespit edilmedi."
    else:
        message = (
            "En sık tespit edilen saldırı: "
            f"<strong>{html.escape(summary['most_common_attack'])}</strong> "
            f"({summary['most_common_count']} kayıt)"
        )

    st.markdown(
        f'<div class="notice-card">{message}</div>',
        unsafe_allow_html=True,
    )

def create_attack_chart(result: pd.DataFrame) -> plt.Figure:
    """Tahmin edilen sınıfların dağılımını gösteren bar grafik üretir."""
    counts = result["Tahmin"].value_counts().sort_values(ascending=True)
    colors = [
        "#7A8C9D" if label == "Benign" else "#1F6F8B"
        for label in counts.index
    ]

    height = max(4.8, 0.42 * len(counts))
    figure, axis = plt.subplots(figsize=(9, height))
    bars = axis.barh(counts.index, counts.values, color=colors)

    axis.set_title(
        "Tahmin Edilen Saldırı Türleri",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel("Kayıt Sayısı")
    axis.set_ylabel("")
    axis.grid(axis="x", alpha=0.2)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    for bar in bars:
        width = int(bar.get_width())
        axis.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f" {width}",
            va="center",
            fontsize=9,
        )

    figure.tight_layout()
    return figure

def create_risk_chart(result: pd.DataFrame) -> plt.Figure:
    """Risk seviyelerinin dağılımını gösteren pasta grafik üretir."""
    risk_order = ["Düşük", "Orta", "Yüksek", "Kritik"]
    counts = (
        result["Risk Seviyesi"]
        .value_counts()
        .reindex(risk_order, fill_value=0)
    )
    counts = counts[counts > 0]
    colors = [RISK_COLORS[level] for level in counts.index]

    figure, axis = plt.subplots(figsize=(7, 5.2))
    wedges, _, _ = axis.pie(
        counts.values,
        labels=counts.index,
        colors=colors,
        autopct=lambda percentage: (
            f"{percentage:.1f}%" if percentage > 0 else ""
        ),
        startangle=90,
        wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
        textprops={"fontsize": 9},
    )
    axis.set_title(
        "Risk Seviyesi Dağılımı",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axis.legend(
        wedges,
        [f"{level}: {counts[level]}" for level in counts.index],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=2,
        frameon=False,
    )
    axis.axis("equal")
    figure.tight_layout()
    return figure

def render_charts(result: pd.DataFrame) -> None:
    """CSV saldırı ve risk grafiklerini iki sütunda gösterir."""
    section_title("Görsel Analiz", "04")
    left_column, right_column = st.columns(2, gap="large")

    with left_column:
        attack_figure = create_attack_chart(result)
        st.pyplot(attack_figure, use_container_width=True)
        plt.close(attack_figure)

    with right_column:
        risk_figure = create_risk_chart(result)
        st.pyplot(risk_figure, use_container_width=True)
        plt.close(risk_figure)

def render_result_table(result: pd.DataFrame) -> None:
    """CSV tahmin sonuçlarını gösterir."""

    section_title("Tahmin Sonuçları", "03")

    summary_columns = [
        "Tahmin",
        "Risk Seviyesi",
        "Güven Skoru (%)",
        "Tahmin Güveni",
        "İkinci Olası Sınıf",
        "İkinci Olasılık (%)",
    ]

    available_columns = [
        column
        for column in summary_columns
        if column in result.columns
    ]

    display_result = result.copy()

    risk_badge_map = {
        "Kritik": "🔴 Kritik",
        "Yüksek": "🟠 Yüksek",
        "Orta": "🟡 Orta",
        "Düşük": "🟢 Düşük",
    }

    display_result["Risk Seviyesi"] = (
        display_result["Risk Seviyesi"]
        .map(risk_badge_map)
        .fillna(display_result["Risk Seviyesi"])
    )

    st.dataframe(
        display_result[available_columns],
        use_container_width=True,
        hide_index=True,
        height=430,
    )   

    with st.expander("Tüm analiz sonuçlarını göster"):
        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True,
        )
def render_risk_table(result: pd.DataFrame) -> None:
    """Tahmin ve risk seviyelerini ayrı bir tabloda gösterir."""

    section_title("Risk Analizi Tablosu", "05")

    risk_table = result.copy()

    risk_badge_map = {
        "Kritik": "🔴 Kritik",
        "Yüksek": "🟠 Yüksek",
        "Orta": "🟡 Orta",
        "Düşük": "🟢 Düşük",
    }

    risk_table["Risk Seviyesi"] = (
        risk_table["Risk Seviyesi"]
        .map(risk_badge_map)
        .fillna(risk_table["Risk Seviyesi"])
    )

    columns = [
        "Tahmin",
        "Risk Seviyesi",
        "Güven Skoru (%)",
        "Tahmin Güveni",
    ]

    available_columns = [
        column
        for column in columns
        if column in risk_table.columns
    ]

    st.dataframe(
        risk_table[available_columns],
        use_container_width=True,
        hide_index=True,
        height=360,
    )

def render_evaluation(summary: dict[str, Any]) -> None:
    """CSV analiz sonuçlarını doğal dilde özetler."""
    section_title("Genel Değerlendirme", "06")

    most_common_text = (
        summary["most_common_attack"]
        if summary["most_common_attack"] is not None
        else "tespit edilmedi"
    )

    evaluation = (
        f"<strong>{summary['total_records']}</strong> kayıt analiz edildi. "
        f"<strong>{summary['attack_count']}</strong> saldırı tespit edildi. "
        f"<strong>{summary['critical_count']}</strong> kritik risk bulundu. "
        "En yaygın saldırı: "
        f"<strong>{html.escape(most_common_text)}</strong>."
    )

    st.markdown(
        f'<div class="evaluation-card">{evaluation}</div>',
        unsafe_allow_html=True,
    )

def render_attack_descriptions(result: pd.DataFrame) -> None:
    """Tespit edilen saldırı türleri için kısa açıklamalar gösterir."""
    section_title("Saldırı Açıklamaları", "07")
    detected_attacks = [
        attack
        for attack in result["Tahmin"].value_counts().index
        if attack != "Benign"
    ]

    if not detected_attacks:
        st.markdown(
            """
            <div class="notice-card">
                Açıklama gerektiren herhangi bir saldırı türü tespit edilmedi.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for start_index in range(0, len(detected_attacks), 2):
        columns = st.columns(2, gap="medium")
        for offset, column in enumerate(columns):
            index = start_index + offset
            if index >= len(detected_attacks):
                continue

            attack = detected_attacks[index]
            count = int((result["Tahmin"] == attack).sum())
            description = ATTACK_DESCRIPTIONS.get(
                attack,
                "Bu saldırı türü için açıklama bulunamadı.",
            )
            with column:
                st.markdown(
                    f"""
                    <div class="description-card">
                        <h4>{html.escape(attack)} ({count} kayıt)</h4>
                        <p>{html.escape(description)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

def collect_recommendations(result: pd.DataFrame) -> list[str]:
    """Tespit edilen saldırılara göre tekrarsız öneriler üretir."""
    detected_attacks = [
        attack
        for attack in result["Tahmin"].unique()
        if attack != "Benign"
    ]

    recommendations: list[str] = []
    for recommendation in GENERAL_RECOMMENDATIONS:
        if recommendation not in recommendations:
            recommendations.append(recommendation)

    for attack in detected_attacks:
        for recommendation in SECURITY_RECOMMENDATIONS.get(attack, []):
            if recommendation not in recommendations:
                recommendations.append(recommendation)

    if not detected_attacks:
        return [
            "Mevcut ağ izleme ve güvenlik politikalarını sürdürün.",
            "Yeni tehditleri yakalamak için IDS/IPS imzalarını güncel tutun.",
            "Periyodik zafiyet taraması ve log incelemesi gerçekleştirin.",
        ]

    return recommendations

def render_recommendations(result: pd.DataFrame) -> None:
    """CSV tahminlerine göre önerilen güvenlik önlemlerini listeler."""
    section_title("Önerilen Güvenlik Önlemleri", "08")
    recommendations = collect_recommendations(result)
    list_items = "".join(
        f"<li>{html.escape(recommendation)}</li>"
        for recommendation in recommendations
    )

    st.markdown(
        f"""
        <div class="recommendation-card">
            <h4>Öncelikli Aksiyonlar</h4>
            <ul>{list_items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_download_button(result: pd.DataFrame) -> None:
    """CSV tahmin sonuçlarını indirme düğmesini gösterir."""
    section_title("Sonuçları CSV Olarak İndir", "09")
    csv_data = result.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Sonuçları CSV Olarak İndir",
        data=csv_data,
        file_name="risk_analizi_sonuclari.csv",
        mime="text/csv",
        use_container_width=True,
    )

def process_uploaded_file(
    uploaded_file: Any,
    model: Any,
) -> pd.DataFrame:
    """Yüklenen CSV dosyasını ilerleme göstergesiyle analiz eder."""
    progress_bar = st.progress(0, text="CSV dosyası hazırlanıyor.")

    with st.spinner("Ağ trafiği kayıtları analiz ediliyor."):
        file_bytes = uploaded_file.getvalue()
        progress_bar.progress(25, text="CSV dosyası okunuyor.")

        dataframe = read_csv_file(file_bytes)
        if dataframe.empty:
            raise ValueError("Yüklenen CSV dosyası boş.")

        progress_bar.progress(55, text="Model özellikleri doğrulanıyor.")
        result = run_prediction(dataframe, model)

        progress_bar.progress(85, text="Rapor hazırlanıyor.")
        summary = calculate_summary(result)
        if summary["total_records"] != len(dataframe):
            raise RuntimeError(
                "Analiz sırasında kayıt sayısı uyuşmazlığı oluştu."
            )

        progress_bar.progress(100, text="Analiz tamamlandı.")

    st.success("Analiz başarıyla tamamlandı.")
    return result

def clear_csv_analysis_state() -> None:
    """Başarısız CSV analizinden kalan geçici oturum verisini temizler."""
    for key in (
        "csv_analysis_signature",
        "csv_analysis_result",
        "csv_analysis_elapsed",
        "csv_analysis_time",
    ):
        st.session_state.pop(key, None)

def render_csv_analysis_tab() -> None:

    """Mevcut Random Forest tabanlı CSV analiz akışını çalıştırır."""
    section_title("CSV Analizi", "CSV")
    st.markdown(
        """
        <div class="notice-card">
            CICIDS2017 veri setindeki 77 model özelliğini içeren CSV dosyasını
            yükleyin. Tahmin ve risk analizi mevcut Random Forest modeliyle
            aynı şekilde çalıştırılır.
        </div>
        """,
        unsafe_allow_html=True,
    )

    model_path = Path(__file__).resolve().parent / MODEL_FILE_NAME
    try:
        model = load_model(str(model_path))
    except FileNotFoundError:
        st.error(
            f"Model dosyası bulunamadı: {MODEL_FILE_NAME}. "
            "Dosyayı app.py ile aynı klasöre yerleştirin."
        )
        return
    except Exception:
        LOGGER.exception("Random Forest modeli yüklenemedi.")
        st.error(
            "Model yüklenemedi. Model dosyasının geçerli ve uygulamayla "
            "uyumlu olduğundan emin olun."
        )
        return

    uploaded_file = st.file_uploader(
        "CSV Dosyası Seçiniz",
        type=["csv"],
        key="csv_file_uploader",
        help=(
            "Modelin kullandığı 77 özelliği içeren CICIDS2017 "
            "CSV dosyasını yükleyin."
        ),
    )

    if uploaded_file is None:
        return

    extension = Path(uploaded_file.name).suffix.lower()
    if extension != ".csv":
        st.error(
            "Geçersiz dosya formatı. CSV analizi için yalnızca .csv "
            "uzantılı dosya yükleyin."
        )
        return

    file_bytes = uploaded_file.getvalue()
    signature = make_file_signature(file_bytes)

    if st.session_state.get("csv_analysis_signature") != signature:
        clear_csv_analysis_state()
        started_at = time.perf_counter()

        try:
            result = process_uploaded_file(uploaded_file, model)
        except MissingColumnsError as exc:
            st.error(
                "CSV dosyasında modelin beklediği aşağıdaki sütunlar eksik:"
            )
            st.code("\n".join(str(column) for column in exc.columns))
            return
        except pd.errors.EmptyDataError:
            st.error("CSV dosyası okunamadı veya dosya içeriği boş.")
            return
        except pd.errors.ParserError:
            st.error(
                "CSV dosyası ayrıştırılamadı. Ayırıcı karakteri ve dosya "
                "yapısını kontrol edin."
            )
            return
        except UnicodeDecodeError:
            st.error(
                "CSV dosyasının karakter kodlaması desteklenmiyor. Dosyayı "
                "UTF-8 olarak kaydedip yeniden deneyin."
            )
            return
        except ValueError as exc:
            st.error(str(exc))
            return
        except Exception:
            LOGGER.exception("CSV analizi sırasında beklenmeyen hata oluştu.")
            st.error(
                "CSV analizi sırasında beklenmeyen bir hata oluştu. "
                "Dosyayı ve model uyumluluğunu kontrol edip yeniden deneyin."
            )
            return

        st.session_state["csv_analysis_signature"] = signature
        st.session_state["csv_analysis_result"] = result
        st.session_state["csv_analysis_elapsed"] = (
            time.perf_counter() - started_at
        )
        st.session_state["csv_analysis_time"] = current_analysis_time()
    else:
        result = st.session_state["csv_analysis_result"]
        st.success("Analiz sonucu hazır.")

    render_file_details(
        file_name=uploaded_file.name,
        file_size=len(file_bytes),
        elapsed_seconds=st.session_state["csv_analysis_elapsed"],
        analysis_time=st.session_state["csv_analysis_time"],
    )

    try:
        summary = calculate_summary(result)
        render_metrics(summary,result)
        if "Güven Skoru (%)" in result.columns:
            low_confidence = int(
            (result["Güven Skoru (%)"] < 70).sum()
            )

        if low_confidence > 0:
            st.warning(
                f"⚠️ {low_confidence} kaydın güven skoru %70'in altında. "
                "Bu kayıtların manuel incelenmesi önerilir."
             )
        render_most_common_attack(summary)
        render_result_table(result)
        render_charts(result)
        render_risk_table(result)
        render_evaluation(summary)
        render_attack_descriptions(result)
        render_recommendations(result)
        render_download_button(result)
    except Exception:
        LOGGER.exception("CSV analiz raporu oluşturulamadı.")
        st.error(
            "CSV analiz raporu görüntülenirken beklenmeyen bir hata oluştu. "
            "Analizi yeniden çalıştırmayı deneyin."
        )
