"""NFStream tabanlı PCAP/PCAPNG Flow analizi."""

from __future__ import annotations

import html
import logging
import tempfile
import time
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from constants import (
    DENSE_TCP_FLOW_MINIMUM,
    DENSE_TCP_RATIO_THRESHOLD,
    HIGH_TRANSFER_AVERAGE_BYTES,
    HIGH_TRANSFER_TOTAL_BYTES,
    PCAP_DEFAULT_COLUMNS,
    PCAP_EXTENSIONS,
    PORT_SCAN_UNIQUE_PORT_THRESHOLD,
    PROTOCOL_NAMES,
)
from helpers import current_analysis_time, format_bytes, make_file_signature
from ui import render_file_details, section_title

LOGGER = logging.getLogger(__name__)


def get_nfstream_class() -> Any:
    """NFStreamer sınıfını yalnızca PCAP analizi gerektiğinde yükler."""
    try:
        from nfstream import NFStreamer
    except ImportError as exc:
        raise RuntimeError(
            "PCAP analizi için 'nfstream' paketi kurulu değil. "
            "Ortamınıza nfstream paketini ekleyin."
        ) from exc

    return NFStreamer

def protocol_name(value: Any) -> str:
    """IP protokol numarasını okunabilir protokol adına dönüştürür."""
    try:
        protocol_number = int(value)
    except (TypeError, ValueError):
        return "Bilinmeyen"

    return PROTOCOL_NAMES.get(
        protocol_number,
        f"IP Protokol {protocol_number}",
    )

def normalize_flow_dataframe(flow_dataframe: pd.DataFrame) -> pd.DataFrame:
    """NFStream çıktısına okunabilir protokol sütunu ekler."""
    normalized = flow_dataframe.copy()
    normalized.columns = [str(column) for column in normalized.columns]

    if "protocol" in normalized.columns:
        normalized["protocol_name"] = normalized["protocol"].map(
            protocol_name
        )
    else:
        normalized["protocol_name"] = "Bilinmeyen"

    key_columns = [
        column
        for column in PCAP_DEFAULT_COLUMNS
        if column in normalized.columns
    ]
    remaining_columns = [
        column
        for column in normalized.columns
        if column not in key_columns
    ]
    return normalized.loc[:, key_columns + remaining_columns]

def process_pcap_uploaded_file(uploaded_file: Any) -> pd.DataFrame:
    """PCAP dosyasını geçici dizinde NFStream ile Flow tablosuna çevirir."""
    extension = Path(uploaded_file.name).suffix.lower()
    if extension not in PCAP_EXTENSIONS:
        raise ValueError(
            "PCAP analizi için yalnızca .pcap veya .pcapng dosyası "
            "yüklenebilir."
        )

    file_bytes = uploaded_file.getvalue()
    if not file_bytes:
        raise ValueError("Yüklenen PCAP dosyası boş.")

    NFStreamer = get_nfstream_class()
    progress_bar = st.progress(0, text="PCAP dosyası hazırlanıyor.")

    with st.spinner("PCAP trafiği NFStream ile analiz ediliyor."):
        progress_bar.progress(15, text="Dosya geçici dizine kaydediliyor.")

        with tempfile.TemporaryDirectory(prefix="pcap_analysis_") as temp_dir:
            temporary_path = Path(temp_dir) / f"capture{extension}"
            temporary_path.write_bytes(file_bytes)

            progress_bar.progress(
                35,
                text="Paketlerden ağ Flow kayıtları çıkarılıyor.",
            )
            streamer = NFStreamer(
                source=str(temporary_path),
                statistical_analysis=True,
            )
            flow_dataframe = streamer.to_pandas(
                columns_to_anonymize=[]
            )

        progress_bar.progress(90, text="Flow tablosu hazırlanıyor.")
        if flow_dataframe.empty:
            raise ValueError(
                "PCAP dosyasında analiz edilebilir herhangi bir Flow "
                "bulunamadı."
            )

        flow_dataframe = normalize_flow_dataframe(flow_dataframe)
        progress_bar.progress(100, text="PCAP analizi tamamlandı.")

    st.success("PCAP analizi başarıyla tamamlandı.")
    return flow_dataframe

def numeric_series(
    dataframe: pd.DataFrame,
    column_name: str,
) -> pd.Series:
    """Bir DataFrame sütununu güvenli biçimde sayısal seriye dönüştürür."""
    if column_name not in dataframe.columns:
        return pd.Series(dtype="float64")

    return pd.to_numeric(dataframe[column_name], errors="coerce")

def calculate_pcap_summary(
    flow_dataframe: pd.DataFrame,
) -> dict[str, Any]:
    """PCAP Flow tablosundan dashboard metriklerini hesaplar."""
    protocol_values = numeric_series(flow_dataframe, "protocol")
    packet_values = numeric_series(
        flow_dataframe,
        "bidirectional_packets",
    ).fillna(0)
    byte_values = numeric_series(
        flow_dataframe,
        "bidirectional_bytes",
    ).fillna(0)
    duration_values = numeric_series(
        flow_dataframe,
        "bidirectional_duration_ms",
    ).dropna()

    average_duration_seconds = 0.0
    if not duration_values.empty:
        average_duration_seconds = float(duration_values.mean() / 1000)

    return {
        "total_flows": int(len(flow_dataframe)),
        "tcp_flows": int((protocol_values == 6).sum()),
        "udp_flows": int((protocol_values == 17).sum()),
        "total_packets": int(packet_values.sum()),
        "total_bytes": int(byte_values.sum()),
        "unique_source_ips": int(
            flow_dataframe.get(
                "src_ip",
                pd.Series(dtype="object"),
            ).nunique(dropna=True)
        ),
        "unique_destination_ips": int(
            flow_dataframe.get(
                "dst_ip",
                pd.Series(dtype="object"),
            ).nunique(dropna=True)
        ),
        "average_duration_seconds": average_duration_seconds,
    }

def render_pcap_metrics(summary: dict[str, Any]) -> None:
    """PCAP istatistiklerini iki satırlı metrik kartlarında gösterir."""
    section_title("PCAP İstatistikleri", "01")

    first_row = st.columns(4)
    first_row[0].metric("Toplam Flow", summary["total_flows"])
    first_row[1].metric("TCP Flow", summary["tcp_flows"])
    first_row[2].metric("UDP Flow", summary["udp_flows"])
    first_row[3].metric(
        "Toplam Paket",
        f"{summary['total_packets']:,}".replace(",", "."),
    )

    second_row = st.columns(4)
    second_row[0].metric(
        "Toplam Byte",
        format_bytes(summary["total_bytes"]),
    )
    second_row[1].metric(
        "Benzersiz Kaynak IP",
        summary["unique_source_ips"],
    )
    second_row[2].metric(
        "Benzersiz Hedef IP",
        summary["unique_destination_ips"],
    )
    second_row[3].metric(
        "Ortalama Flow Süresi",
        f"{summary['average_duration_seconds']:.2f} sn",
    )

def empty_chart(title: str, message: str) -> plt.Figure:
    """Grafik verisi olmadığında açıklayıcı boş grafik oluşturur."""
    figure, axis = plt.subplots(figsize=(8, 4.8))
    axis.set_title(title, fontsize=13, fontweight="bold", pad=14)
    axis.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        transform=axis.transAxes,
    )
    axis.axis("off")
    figure.tight_layout()
    return figure

def style_chart_axis(axis: Any) -> None:
    """Matplotlib eksenlerinde ortak profesyonel görünümü uygular."""
    axis.grid(axis="y", alpha=0.18)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

def create_protocol_chart(flow_dataframe: pd.DataFrame) -> plt.Figure:
    """En çok kullanılan taşıma protokollerini gösterir."""
    if "protocol_name" not in flow_dataframe.columns:
        return empty_chart(
            "En Çok Kullanılan Protokoller",
            "Protokol bilgisi bulunamadı.",
        )

    counts = flow_dataframe["protocol_name"].fillna("Bilinmeyen")
    counts = counts.value_counts().head(10)
    figure, axis = plt.subplots(figsize=(8, 4.8))
    bars = axis.bar(counts.index.astype(str), counts.values, color="#2563EB")
    axis.set_title(
        "En Çok Kullanılan Protokoller",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel("Protokol")
    axis.set_ylabel("Flow Sayısı")
    axis.tick_params(axis="x", rotation=35)
    style_chart_axis(axis)

    for bar in bars:
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{int(bar.get_height())}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    figure.tight_layout()
    return figure

def create_top_talkers_chart(flow_dataframe: pd.DataFrame) -> plt.Figure:
    """Flow sayısına göre en çok konuşan ilk 10 IP adresini gösterir."""
    ip_series = []
    for column_name in ("src_ip", "dst_ip"):
        if column_name in flow_dataframe.columns:
            ip_series.append(flow_dataframe[column_name].dropna().astype(str))

    if not ip_series:
        return empty_chart(
            "En Çok Konuşan İlk 10 IP",
            "IP bilgisi bulunamadı.",
        )

    counts = pd.concat(ip_series, ignore_index=True).value_counts().head(10)
    counts = counts.sort_values(ascending=True)

    figure, axis = plt.subplots(figsize=(8, 4.8))
    axis.barh(counts.index, counts.values, color="#0891B2")
    axis.set_title(
        "En Çok Konuşan İlk 10 IP",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel("Flow Katılım Sayısı")
    axis.set_ylabel("")
    axis.grid(axis="x", alpha=0.18)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    figure.tight_layout()
    return figure

def create_top_ports_chart(flow_dataframe: pd.DataFrame) -> plt.Figure:
    """En sık kullanılan hedef portları gösterir."""
    ports = numeric_series(flow_dataframe, "dst_port").dropna()
    ports = ports[ports > 0].astype(int)
    if ports.empty:
        return empty_chart(
            "En Çok Kullanılan Portlar",
            "Hedef port bilgisi bulunamadı.",
        )

    counts = ports.value_counts().head(12)
    figure, axis = plt.subplots(figsize=(8, 4.8))
    axis.bar(counts.index.astype(str), counts.values, color="#0F766E")
    axis.set_title(
        "En Çok Kullanılan Portlar",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel("Hedef Port")
    axis.set_ylabel("Flow Sayısı")
    axis.tick_params(axis="x", rotation=35)
    style_chart_axis(axis)
    figure.tight_layout()
    return figure

def create_duration_histogram(flow_dataframe: pd.DataFrame) -> plt.Figure:
    """Flow sürelerini saniye cinsinden histogram olarak gösterir."""
    duration_seconds = numeric_series(
        flow_dataframe,
        "bidirectional_duration_ms",
    ).dropna() / 1000

    if duration_seconds.empty:
        return empty_chart(
            "Flow Süreleri Histogramı",
            "Flow süresi bilgisi bulunamadı.",
        )

    figure, axis = plt.subplots(figsize=(8, 4.8))
    axis.hist(duration_seconds, bins=30, color="#7C3AED", alpha=0.88)
    axis.set_title(
        "Flow Süreleri Histogramı",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel("Süre (saniye)")
    axis.set_ylabel("Flow Sayısı")
    style_chart_axis(axis)
    figure.tight_layout()
    return figure

def create_packet_histogram(flow_dataframe: pd.DataFrame) -> plt.Figure:
    """Flow başına paket sayılarını histogram olarak gösterir."""
    packet_counts = numeric_series(
        flow_dataframe,
        "bidirectional_packets",
    ).dropna()

    if packet_counts.empty:
        return empty_chart(
            "Paket Sayısı Histogramı",
            "Paket sayısı bilgisi bulunamadı.",
        )

    figure, axis = plt.subplots(figsize=(12, 4.8))
    axis.hist(packet_counts, bins=35, color="#B45309", alpha=0.88)
    axis.set_title(
        "Paket Sayısı Histogramı",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    axis.set_xlabel("Flow Başına Paket Sayısı")
    axis.set_ylabel("Flow Sayısı")
    style_chart_axis(axis)
    figure.tight_layout()
    return figure

def render_pcap_charts(flow_dataframe: pd.DataFrame) -> None:
    """PCAP grafiklerini responsive dashboard düzeninde gösterir."""
    section_title("Trafik Grafikleri", "02")

    first_left, first_right = st.columns(2, gap="large")
    with first_left:
        figure = create_protocol_chart(flow_dataframe)
        st.pyplot(figure, use_container_width=True)
        plt.close(figure)
    with first_right:
        figure = create_top_talkers_chart(flow_dataframe)
        st.pyplot(figure, use_container_width=True)
        plt.close(figure)

    second_left, second_right = st.columns(2, gap="large")
    with second_left:
        figure = create_top_ports_chart(flow_dataframe)
        st.pyplot(figure, use_container_width=True)
        plt.close(figure)
    with second_right:
        figure = create_duration_histogram(flow_dataframe)
        st.pyplot(figure, use_container_width=True)
        plt.close(figure)

    figure = create_packet_histogram(flow_dataframe)
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)

def evaluate_pcap_security(
    flow_dataframe: pd.DataFrame,
    summary: dict[str, Any],
) -> list[dict[str, str]]:
    """PCAP istatistiklerine basit, açıklanabilir güvenlik kuralları uygular."""
    findings: list[dict[str, str]] = []
    total_flows = summary["total_flows"]

    if total_flows > 0:
        tcp_ratio = summary["tcp_flows"] / total_flows
        if (
            summary["tcp_flows"] >= DENSE_TCP_FLOW_MINIMUM
            and tcp_ratio >= DENSE_TCP_RATIO_THRESHOLD
        ):
            findings.append(
                {
                    "level": "info",
                    "title": "Yoğun TCP trafiği",
                    "message": (
                        f"Flow kayıtlarının %{tcp_ratio * 100:.1f} kadarı "
                        "TCP trafiğinden oluşuyor. Trafik yoğunluğu ve "
                        "bağlantı davranışları izlenmelidir."
                    ),
                }
            )

    required_columns = {"src_ip", "dst_port"}
    if required_columns.issubset(flow_dataframe.columns):
        scan_frame = flow_dataframe.loc[:, ["src_ip", "dst_port"]].copy()
        scan_frame["dst_port"] = pd.to_numeric(
            scan_frame["dst_port"],
            errors="coerce",
        )
        scan_frame = scan_frame.dropna(subset=["src_ip", "dst_port"])
        unique_ports = (
            scan_frame.groupby("src_ip")["dst_port"]
            .nunique()
            .sort_values(ascending=False)
        )
        suspicious_sources = unique_ports[
            unique_ports >= PORT_SCAN_UNIQUE_PORT_THRESHOLD
        ]

        if not suspicious_sources.empty:
            source_preview = ", ".join(
                f"{source} ({int(port_count)} port)"
                for source, port_count in suspicious_sources.head(3).items()
            )
            findings.append(
                {
                    "level": "danger",
                    "title": "Olası port taraması",
                    "message": (
                        "Aynı kaynak IP adresinden çok sayıda farklı hedef "
                        f"porta bağlantı gözlendi: {source_preview}. Bu durum "
                        "keşif veya port taraması davranışıyla uyumlu olabilir."
                    ),
                }
            )

    average_bytes = 0.0
    if total_flows > 0:
        average_bytes = summary["total_bytes"] / total_flows

    if (
        summary["total_bytes"] >= HIGH_TRANSFER_TOTAL_BYTES
        or average_bytes >= HIGH_TRANSFER_AVERAGE_BYTES
    ):
        findings.append(
            {
                "level": "warning",
                "title": "Yoğun veri transferi",
                "message": (
                    f"Toplam {format_bytes(summary['total_bytes'])} veri "
                    "aktarımı gözlendi. Büyük hacimli Flow kayıtlarının "
                    "kaynak ve hedefleri ayrıca incelenmelidir."
                ),
            }
        )

    return findings

def render_security_assessment(
    findings: list[dict[str, str]],
) -> None:
    """Rule-based PCAP bulgularını açıklayıcı bilgi kutularında gösterir."""
    section_title("Güvenlik Değerlendirmesi", "03")
    st.info(
    """
    ### 📡 PCAP Flow Analysis & Security Assessment

    Bu modül **Makine Öğrenmesi modeli çalıştırmaz**.
    Analizler NFStream tarafından çıkarılan ağ akışları üzerinde
    uygulanan kural tabanlı güvenlik değerlendirmelerine dayanır.       

    PCAP dosyası **NFStream** ile ağ akışlarına (network flows) dönüştürülür ve aşağıdaki analizler gerçekleştirilir:

    - 📊 Flow Statistics
    - 🌐 Protocol Distribution
    - 🔌 Port Analysis
    - 🖥️ IP Analysis
    - 🛡️ Rule-Based Security Assessment

    > **Not:** Bu bölümdeki sonuçlar saldırı sınıflandırması değil,
    flow istatistiklerinden elde edilen olası güvenlik bulgularıdır.
    """
    )

    if not findings:
        st.success(
            "Tanımlı temel kurallara göre dikkat gerektiren belirgin bir "
            "trafik davranışı bulunmadı."
        )
        return

    class_map = {
        "info": "security-info",
        "warning": "security-warning",
        "danger": "security-danger",
    }
    for finding in findings:
        card_class = class_map.get(finding["level"], "security-info")
        st.markdown(
            f"""
            <div class="security-card {card_class}">
                <strong>{html.escape(finding['title'])}</strong>
                {html.escape(finding['message'])}
            </div>
            """,
            unsafe_allow_html=True,
        )

def searchable_columns(flow_dataframe: pd.DataFrame) -> list[str]:
    """Flow tablosu aramasında kullanılacak anlamlı sütunları döndürür."""
    candidates = [
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port",
        "protocol_name",
        "application_name",
        "application_category_name",
        "requested_server_name",
        "user_agent",
    ]
    return [
        column
        for column in candidates
        if column in flow_dataframe.columns
    ]

def filter_flow_dataframe(
    flow_dataframe: pd.DataFrame,
    search_text: str,
    selected_protocols: list[str],
    minimum_packets: int,
    minimum_bytes: int,
) -> pd.DataFrame:
    """Flow tablosuna arama ve dashboard filtrelerini uygular."""
    filtered = flow_dataframe.copy()

    if selected_protocols and "protocol_name" in filtered.columns:
        filtered = filtered[
            filtered["protocol_name"].isin(selected_protocols)
        ]

    if minimum_packets > 0 and "bidirectional_packets" in filtered.columns:
        packet_values = pd.to_numeric(
            filtered["bidirectional_packets"],
            errors="coerce",
        ).fillna(0)
        filtered = filtered[packet_values >= minimum_packets]

    if minimum_bytes > 0 and "bidirectional_bytes" in filtered.columns:
        byte_values = pd.to_numeric(
            filtered["bidirectional_bytes"],
            errors="coerce",
        ).fillna(0)
        filtered = filtered[byte_values >= minimum_bytes]

    normalized_search = search_text.strip()
    if normalized_search:
        columns = searchable_columns(filtered)
        if columns:
            search_mask = pd.Series(False, index=filtered.index)
            for column in columns:
                search_mask |= (
                    filtered[column]
                    .astype(str)
                    .str.contains(
                        normalized_search,
                        case=False,
                        na=False,
                        regex=False,
                    )
                )
            filtered = filtered[search_mask]

    return filtered

def render_flow_table(flow_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Arama, filtreleme ve sıralama destekli Flow tablosunu gösterir."""
    section_title("Flow Tablosu", "04")

    search_text = st.text_input(
        "Flow tablosunda ara",
        key="pcap_flow_search",
        placeholder="IP, port, protokol, uygulama veya sunucu adı arayın",
    )

    filter_column_1, filter_column_2, filter_column_3 = st.columns(3)
    protocol_options = []
    if "protocol_name" in flow_dataframe.columns:
        protocol_options = sorted(
            flow_dataframe["protocol_name"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    with filter_column_1:
        selected_protocols = st.multiselect(
            "Protokol Filtresi",
            options=protocol_options,
            key="pcap_protocol_filter",
        )
    with filter_column_2:
        minimum_packets = int(
            st.number_input(
                "Minimum Paket Sayısı",
                min_value=0,
                value=0,
                step=1,
                key="pcap_minimum_packets",
            )
        )
    with filter_column_3:
        minimum_bytes = int(
            st.number_input(
                "Minimum Byte",
                min_value=0,
                value=0,
                step=1024,
                key="pcap_minimum_bytes",
            )
        )

    filtered = filter_flow_dataframe(
        flow_dataframe=flow_dataframe,
        search_text=search_text,
        selected_protocols=selected_protocols,
        minimum_packets=minimum_packets,
        minimum_bytes=minimum_bytes,
    )

    available_columns = list(flow_dataframe.columns)
    default_columns = [
        column
        for column in PCAP_DEFAULT_COLUMNS
        if column in available_columns
    ]
    visible_columns = st.multiselect(
        "Tabloda Gösterilecek Sütunlar",
        options=available_columns,
        default=default_columns,
        key="pcap_visible_columns",
    )
    if not visible_columns:
        visible_columns = default_columns or available_columns[:10]

    sort_column_1, sort_column_2 = st.columns([3, 1])
    with sort_column_1:
        sort_column = st.selectbox(
            "Sıralama Sütunu",
            options=visible_columns,
            key="pcap_sort_column",
        )
    with sort_column_2:
        descending = st.checkbox(
            "Azalan sırala",
            value=True,
            key="pcap_sort_descending",
        )

    if sort_column:
        try:
            filtered = filtered.sort_values(
                by=sort_column,
                ascending=not descending,
                kind="mergesort",
                na_position="last",
            )
        except (TypeError, ValueError):
            sortable_values = filtered[sort_column].astype(str)
            ordered_index = sortable_values.sort_values(
                ascending=not descending,
                kind="mergesort",
            ).index
            filtered = filtered.loc[ordered_index]

    total_flow_text = f"{len(flow_dataframe):,}".replace(",", ".")
    filtered_flow_text = f"{len(filtered):,}".replace(",", ".")
    st.caption(
        f"{total_flow_text} Flow içinden "
        f"{filtered_flow_text} kayıt gösteriliyor."
    )
    st.dataframe(
        filtered.loc[:, visible_columns],
        use_container_width=True,
        hide_index=True,
        height=520,
    )
    return filtered

def top_talkers(flow_dataframe: pd.DataFrame) -> pd.Series:
    """Rapor için en çok Flowa katılan IP adreslerini hesaplar."""
    series_list = []
    for column in ("src_ip", "dst_ip"):
        if column in flow_dataframe.columns:
            series_list.append(flow_dataframe[column].dropna().astype(str))

    if not series_list:
        return pd.Series(dtype="int64")

    return pd.concat(series_list, ignore_index=True).value_counts().head(10)

def build_pcap_report(
    flow_dataframe: pd.DataFrame,
    summary: dict[str, Any],
    findings: list[dict[str, str]],
    file_name: str,
    analysis_time: str,
) -> pd.DataFrame:
    """PCAP özetini, en sık değerleri ve güvenlik bulgularını CSVye hazırlar."""
    rows: list[dict[str, str]] = [
        {"Bölüm": "Dosya", "Metrik": "Dosya Adı", "Değer": file_name},
        {
            "Bölüm": "Dosya",
            "Metrik": "Analiz Zamanı",
            "Değer": analysis_time,
        },
        {
            "Bölüm": "Özet",
            "Metrik": "Toplam Flow",
            "Değer": str(summary["total_flows"]),
        },
        {
            "Bölüm": "Özet",
            "Metrik": "TCP Flow",
            "Değer": str(summary["tcp_flows"]),
        },
        {
            "Bölüm": "Özet",
            "Metrik": "UDP Flow",
            "Değer": str(summary["udp_flows"]),
        },
        {
            "Bölüm": "Özet",
            "Metrik": "Toplam Paket",
            "Değer": str(summary["total_packets"]),
        },
        {
            "Bölüm": "Özet",
            "Metrik": "Toplam Byte",
            "Değer": str(summary["total_bytes"]),
        },
        {
            "Bölüm": "Özet",
            "Metrik": "Benzersiz Kaynak IP",
            "Değer": str(summary["unique_source_ips"]),
        },
        {
            "Bölüm": "Özet",
            "Metrik": "Benzersiz Hedef IP",
            "Değer": str(summary["unique_destination_ips"]),
        },
        {
            "Bölüm": "Özet",
            "Metrik": "Ortalama Flow Süresi (sn)",
            "Değer": f"{summary['average_duration_seconds']:.6f}",
        },
    ]

    if "protocol_name" in flow_dataframe.columns:
        protocol_counts = (
            flow_dataframe["protocol_name"]
            .fillna("Bilinmeyen")
            .value_counts()
            .head(10)
        )
        for protocol, count in protocol_counts.items():
            rows.append(
                {
                    "Bölüm": "Protokoller",
                    "Metrik": str(protocol),
                    "Değer": str(int(count)),
                }
            )

    for ip_address, count in top_talkers(flow_dataframe).items():
        rows.append(
            {
                "Bölüm": "En Çok Konuşan IP",
                "Metrik": str(ip_address),
                "Değer": str(int(count)),
            }
        )

    ports = numeric_series(flow_dataframe, "dst_port").dropna()
    ports = ports[ports > 0].astype(int).value_counts().head(10)
    for port, count in ports.items():
        rows.append(
            {
                "Bölüm": "Hedef Portlar",
                "Metrik": str(int(port)),
                "Değer": str(int(count)),
            }
        )

    if findings:
        for finding in findings:
            rows.append(
                {
                    "Bölüm": "Güvenlik Değerlendirmesi",
                    "Metrik": finding["title"],
                    "Değer": finding["message"],
                }
            )
    else:
        rows.append(
            {
                "Bölüm": "Güvenlik Değerlendirmesi",
                "Metrik": "Sonuç",
                "Değer": "Tanımlı temel kurallar tetiklenmedi.",
            }
        )

    return pd.DataFrame(rows)

def render_pcap_downloads(
    filtered_flow_dataframe: pd.DataFrame,
    report_dataframe: pd.DataFrame,
    original_file_name: str,
) -> None:
    """Flow tablosu ve PCAP raporu için ayrı CSV indirme düğmeleri gösterir."""
    section_title("PCAP Çıktılarını İndir", "05")
    safe_stem = Path(original_file_name).stem or "pcap_analizi"
    left_column, right_column = st.columns(2, gap="large")

    with left_column:
        st.download_button(
            label="Flow Tablosunu CSV Olarak İndir",
            data=filtered_flow_dataframe.to_csv(index=False).encode(
                "utf-8-sig"
            ),
            file_name=f"{safe_stem}_flow_tablosu.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with right_column:
        st.download_button(
            label="PCAP Analiz Raporunu CSV Olarak İndir",
            data=report_dataframe.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{safe_stem}_analiz_raporu.csv",
            mime="text/csv",
            use_container_width=True,
        )

def clear_pcap_analysis_state() -> None:
    """Başarısız PCAP analizinden kalan oturum verisini temizler."""
    for key in (
        "pcap_analysis_signature",
        "pcap_flow_dataframe",
        "pcap_analysis_elapsed",
        "pcap_analysis_time",
        "pcap_flow_search",
        "pcap_protocol_filter",
        "pcap_minimum_packets",
        "pcap_minimum_bytes",
        "pcap_visible_columns",
        "pcap_sort_column",
        "pcap_sort_descending",
    ):
        st.session_state.pop(key, None)

def render_pcap_analysis_tab() -> None:
    """NFStream tabanlı PCAP ve PCAPNG analiz sekmesini çalıştırır."""
    section_title("PCAP Analizi", "PCAP")
    st.markdown(
        """
        <div class="notice-card">
            .pcap veya .pcapng dosyanızı yükleyin. Dosya geçici bir dizinde
            işlenir, NFStream ile istatistiksel Flow özellikleri çıkarılır ve
            işlem tamamlandığında geçici dosya otomatik olarak silinir.
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "PCAP veya PCAPNG Dosyası Seçiniz",
        type=["pcap", "pcapng"],
        key="pcap_file_uploader",
        help="Çevrim dışı analiz için .pcap veya .pcapng dosyası yükleyin.",
    )

    if uploaded_file is None:
        return

    extension = Path(uploaded_file.name).suffix.lower()
    if extension not in PCAP_EXTENSIONS:
        st.error(
            "Geçersiz dosya formatı. PCAP analizi için yalnızca .pcap veya "
            ".pcapng uzantılı dosya yükleyin."
        )
        return

    file_bytes = uploaded_file.getvalue()
    signature = make_file_signature(file_bytes)

    if st.session_state.get("pcap_analysis_signature") != signature:
        clear_pcap_analysis_state()
        started_at = time.perf_counter()

        try:
            flow_dataframe = process_pcap_uploaded_file(uploaded_file)
        except RuntimeError as exc:
            st.error(str(exc))
            return
        except ValueError as exc:
            st.error(str(exc))
            return
        except PermissionError:
            LOGGER.exception("PCAP dosyası geçici dizine yazılamadı.")
            st.error(
                "PCAP dosyası geçici dizine yazılamadı. Uygulamanın dosya "
                "sistemi izinlerini kontrol edin."
            )
            return
        except Exception:
            LOGGER.exception("PCAP analizi sırasında beklenmeyen hata oluştu.")
            st.error(
                "PCAP analizi tamamlanamadı. Dosyanın bozuk olmadığını ve "
                "NFStream ortamının doğru kurulduğunu kontrol edin."
            )
            return

        st.session_state["pcap_analysis_signature"] = signature
        st.session_state["pcap_flow_dataframe"] = flow_dataframe
        st.session_state["pcap_analysis_elapsed"] = (
            time.perf_counter() - started_at
        )
        st.session_state["pcap_analysis_time"] = current_analysis_time()
    else:
        flow_dataframe = st.session_state["pcap_flow_dataframe"]
        st.success("PCAP analiz sonucu hazır.")

    render_file_details(
        file_name=uploaded_file.name,
        file_size=len(file_bytes),
        elapsed_seconds=st.session_state["pcap_analysis_elapsed"],
        analysis_time=st.session_state["pcap_analysis_time"],
    )

    try:
        summary = calculate_pcap_summary(flow_dataframe)
        findings = evaluate_pcap_security(flow_dataframe, summary)

        render_pcap_metrics(summary)
        render_pcap_charts(flow_dataframe)
        render_security_assessment(findings)
        filtered_flows = render_flow_table(flow_dataframe)
        report_dataframe = build_pcap_report(
            flow_dataframe=flow_dataframe,
            summary=summary,
            findings=findings,
            file_name=uploaded_file.name,
            analysis_time=st.session_state["pcap_analysis_time"],
        )
        render_pcap_downloads(
            filtered_flow_dataframe=filtered_flows,
            report_dataframe=report_dataframe,
            original_file_name=uploaded_file.name,
        )
    except Exception:
        LOGGER.exception("PCAP analiz raporu oluşturulamadı.")
        st.error(
            "PCAP analiz raporu görüntülenirken beklenmeyen bir hata oluştu. "
            "Analizi yeniden çalıştırmayı deneyin."
        )
