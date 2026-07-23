"""Streamlit sayfa iskeleti ve ortak arayüz bileşenleri."""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from constants import APP_TITLE
from helpers import format_bytes


def configure_page() -> None:
    """Sayfa ayarlarını ve koyu temayla uyumlu CSS kurallarını uygular."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        :root {
            --app-primary: var(--primary-color, #2563EB);
            --app-background: var(--background-color, #F4F7FB);
            --app-surface: var(--secondary-background-color, #FFFFFF);
            --app-text: var(--text-color, #17212B);
            --app-border: rgba(128, 142, 160, 0.24);
            --app-shadow: 0 12px 30px rgba(15, 23, 42, 0.10);
            --app-blue: #2563EB;
            --app-cyan: #0891B2;
            --app-green: #15803D;
            --app-amber: #B45309;
            --app-red: #B91C1C;
        }

        .stApp {
            background: var(--app-background);
            color: var(--app-text);
        }

        .block-container {
            max-width: 1480px;
            padding-top: 1.7rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0B2033 0%, #123C5A 100%);
        }

        [data-testid="stSidebar"] * {
            color: #F5F8FC;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.16);
        }

        .sidebar-title {
            margin: 0.9rem 0 0.25rem;
            font-size: 1.02rem;
            font-weight: 750;
            letter-spacing: 0.02em;
        }

        .sidebar-card {
            margin: 0.45rem 0 1rem;
            padding: 0.85rem 0.95rem;
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.07);
        }

        .sidebar-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.34rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.09);
            font-size: 0.90rem;
        }

        .sidebar-row:last-child {
            border-bottom: none;
        }

        .sidebar-row span:last-child {
            font-weight: 700;
            text-align: right;
        }

        .sidebar-list {
            margin: 0;
            padding-left: 1.25rem;
            line-height: 1.85;
            font-size: 0.90rem;
        }

        .hero-card {
            margin-bottom: 1.15rem;
            padding: 1.65rem 1.75rem;
            border: 1px solid var(--app-border);
            border-radius: 20px;
            background:
                linear-gradient(135deg, var(--app-surface) 0%,
                rgba(37, 99, 235, 0.09) 100%);
            box-shadow: var(--app-shadow);
        }

        .hero-card h1 {
            margin: 0;
            color: var(--app-text);
            font-size: clamp(1.75rem, 3vw, 2.65rem);
            line-height: 1.15;
        }

        .hero-card p {
            max-width: 940px;
            margin: 0.75rem 0 0;
            color: var(--app-text);
            opacity: 0.74;
            font-size: 1.01rem;
            line-height: 1.65;
        }

        .section-title {
            display: flex;
            align-items: center;
            gap: 0.62rem;
            margin: 1.55rem 0 0.75rem;
            color: var(--app-text);
            font-size: 1.24rem;
            font-weight: 760;
        }

        .section-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 31px;
            height: 31px;
            border-radius: 9px;
            background: rgba(37, 99, 235, 0.13);
            color: var(--app-blue);
            font-size: 0.88rem;
            font-weight: 800;
        }

        .notice-card,
        .evaluation-card,
        .description-card,
        .recommendation-card,
        .security-card,
        .about-card,
        .file-card {
            border: 1px solid var(--app-border);
            border-radius: 16px;
            background: var(--app-surface);
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
        }

        .notice-card {
            padding: 1rem 1.1rem;
            border-left: 5px solid var(--app-cyan);
            line-height: 1.6;
        }

        .evaluation-card {
            padding: 1.15rem 1.25rem;
            border-left: 5px solid var(--app-blue);
            line-height: 1.75;
        }

        .description-card,
        .recommendation-card {
            height: 100%;
            padding: 1rem 1.1rem;
        }

        .description-card h4,
        .recommendation-card h4 {
            margin: 0 0 0.5rem;
            color: var(--app-text);
            font-size: 1rem;
        }

        .description-card p,
        .recommendation-card li {
            color: var(--app-text);
            opacity: 0.75;
            line-height: 1.55;
        }

        .recommendation-card ul {
            margin: 0;
            padding-left: 1.2rem;
        }

        .file-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin: 0.8rem 0 0.4rem;
        }

        .file-card {
            min-width: 0;
            padding: 0.9rem 1rem;
        }

        .file-card-label {
            color: var(--app-text);
            opacity: 0.65;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .file-card-value {
            margin-top: 0.35rem;
            color: var(--app-text);
            font-size: 0.96rem;
            font-weight: 700;
            overflow-wrap: anywhere;
        }

        .security-card {
            margin-bottom: 0.7rem;
            padding: 0.95rem 1.05rem;
            line-height: 1.58;
        }

        .security-card strong {
            display: block;
            margin-bottom: 0.25rem;
        }

        .security-warning {
            border-left: 5px solid var(--app-amber);
        }

        .security-danger {
            border-left: 5px solid var(--app-red);
        }

        .security-info {
            border-left: 5px solid var(--app-cyan);
        }

        .about-card {
            margin-top: 2.1rem;
            padding: 1.3rem 1.4rem;
            text-align: center;
        }

        .about-title {
            margin-bottom: 0.55rem;
            font-size: 1.05rem;
            font-weight: 760;
        }

        .about-meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5rem;
        }

        .about-chip {
            padding: 0.38rem 0.65rem;
            border: 1px solid var(--app-border);
            border-radius: 999px;
            background: rgba(37, 99, 235, 0.08);
            font-size: 0.84rem;
            font-weight: 650;
        }

        [data-testid="stMetric"] {
            min-height: 122px;
            padding: 1rem 1.05rem;
            border: 1px solid var(--app-border);
            border-radius: 16px;
            background: var(--app-surface);
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
        }

        [data-testid="stMetricLabel"] {
            color: var(--app-text);
            opacity: 0.68;
            font-weight: 650;
        }

        [data-testid="stMetricValue"] {
            color: var(--app-text);
        }

        [data-testid="stFileUploader"] {
            padding: 0.45rem;
            border: 1px solid var(--app-border);
            border-radius: 16px;
            background: var(--app-surface);
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }

        [data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid var(--app-border);
            border-radius: 14px;
            background: var(--app-surface);
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
        }

        .stDownloadButton > button {
            min-height: 46px;
            width: 100%;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #1D4ED8, #0E7490);
            color: #FFFFFF;
            font-weight: 700;
            box-shadow: 0 8px 20px rgba(30, 64, 175, 0.22);
        }

        .stDownloadButton > button:hover {
            border: none;
            color: #FFFFFF;
            transform: translateY(-1px);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            padding: 0.35rem;
            border: 1px solid var(--app-border);
            border-radius: 14px;
            background: var(--app-surface);
        }

        /* Streamlit sekmeleri: pasif sekmeler de her zaman görünür. */
        .stTabs [data-baseweb="tab"] {
            min-height: 46px;
            padding: 0.65rem 1.15rem;
            border-radius: 10px;
            background-color: #E2E8F0 !important;
            color: #0F172A !important;
            opacity: 1 !important;
            font-weight: 700 !important;
        }

        /* Streamlit, sekme metnini iç içe p/span elemanlarında tutabilir. */
        .stTabs [data-baseweb="tab"] *,
        .stTabs [data-baseweb="tab"] p,
        .stTabs [data-baseweb="tab"] span {
            color: #0F172A !important;
            opacity: 1 !important;
            font-weight: 700 !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #1D4ED8, #0E7490) !important;
            color: #FFFFFF !important;
            opacity: 1 !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] *,
        .stTabs [data-baseweb="tab"][aria-selected="true"] p,
        .stTabs [data-baseweb="tab"][aria-selected="true"] span {
            color: #FFFFFF !important;
            opacity: 1 !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #CBD5E1 !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"]:hover {
            background: linear-gradient(135deg, #1E40AF, #0F6B82) !important;
        }

        @media (max-width: 900px) {
            .file-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 640px) {
            .block-container {
                padding-top: 1rem;
            }

            .hero-card {
                padding: 1.2rem;
                border-radius: 16px;
            }

            .file-grid {
                grid-template-columns: 1fr;
            }

            [data-testid="stMetric"] {
                min-height: auto;
            }
        }
    /* STREAMLIT 1.60 TAB DÜZELTMESİ */

    button[role="tab"] {
        background: #E2E8F0 !important;
        color: #111827 !important;
    }

    button[role="tab"] p {
        color: #111827 !important;
        opacity: 1 !important;
        font-weight: 700 !important;
     -webkit-text-fill-color: #111827 !important;
    }

    /* Aktif sekme */

    button[role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg,#1D4ED8,#0E7490) !important;
    }

    button[role="tab"][aria-selected="true"] p {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }   
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_sidebar() -> None:
    """Proje, model, kullanım ve dosya formatı bilgilerini gösterir."""
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-title">Proje Bilgisi</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="sidebar-card">
                <div class="sidebar-row">
                    <span>Proje</span><span>{APP_TITLE}</span>
                </div>
                <div class="sidebar-row">
                    <span>Program</span><span>Microsoft AI Innovators</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-title">Model Bilgisi</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-row">
                    <span>Model</span><span>Random Forest</span>
                </div>
                <div class="sidebar-row">
                    <span>Veri Seti</span><span>CICIDS2017</span>
                </div>
                <div class="sidebar-row">
                    <span>Özellik Sayısı</span><span>77</span>
                </div>
                <div class="sidebar-row">
                    <span>Sınıf Sayısı</span><span>15</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-title">Kullanım Kılavuzu</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="sidebar-card">
                <ol class="sidebar-list">
                    <li>Analiz sekmesini seçin.</li>
                    <li>Desteklenen dosyayı yükleyin.</li>
                    <li>Analiz sonuçlarını ve grafikleri inceleyin.</li>
                    <li>Oluşturulan CSV raporunu indirin.</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-title">Desteklenen Dosya Formatları</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-row">
                    <span>Model Analizi</span><span>.csv</span>
                </div>
                <div class="sidebar-row">
                    <span>Paket Analizi</span><span>.pcap, .pcapng</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_header() -> None:
    """Uygulamanın ana başlığını ve kapsam açıklamasını gösterir."""
    st.markdown(
        f"""
        <section class="hero-card">
            <h1>{APP_TITLE}</h1>
            <p>
                CICIDS2017 özelliklerini içeren CSV kayıtlarını Random Forest
                modeliyle sınıflandırın veya PCAP trafiğini NFStream tabanlı
                akış istatistikleriyle inceleyin. İki analiz modu birbirinden
                bağımsız çalışır ve sonuçlarını ayrı raporlar hâlinde sunar.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

def section_title(title: str, icon: str = "◆") -> None:
    """Bölüm başlıkları için ortak, ikonlu bileşeni oluşturur."""
    st.markdown(
        (
            '<div class="section-title">'
            f'<span class="section-icon">{html.escape(icon)}</span>'
            f"<span>{html.escape(title)}</span>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

def render_file_details(
    file_name: str,
    file_size: int,
    elapsed_seconds: float,
    analysis_time: str,
) -> None:
    """Yüklenen dosya ve analiz zamanlaması bilgilerini kartlarda gösterir."""
    extension = Path(file_name).suffix.lower() or "Bilinmiyor"
    cards = [
        ("Dosya Adı", file_name),
        ("Dosya Uzantısı", extension),
        ("Dosya Boyutu", format_bytes(file_size)),
        ("Analiz Süresi", f"{elapsed_seconds:.2f} saniye"),
    ]
    card_html = "".join(
        (
            '<div class="file-card">'
            f'<div class="file-card-label">{html.escape(label)}</div>'
            f'<div class="file-card-value">{html.escape(value)}</div>'
            "</div>"
        )
        for label, value in cards
    )

    st.markdown(
        f'<div class="file-grid">{card_html}</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Son analiz zamanı: {analysis_time}")

def render_about() -> None:
    """Uygulama teknoloji ve program bilgilerini sayfa altında gösterir."""
    st.markdown(
        f"""
        <div class="about-card">
            <div class="about-title">{APP_TITLE}</div>
            <div class="about-meta">
                <span class="about-chip">Microsoft AI Innovators Staj Programı</span>
                <span class="about-chip">Random Forest</span>
                <span class="about-chip">CICIDS2017</span>
                <span class="about-chip">Streamlit</span>
                <span class="about-chip">NFStream</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )