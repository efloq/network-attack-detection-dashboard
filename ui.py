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
            font-size: 1.5rem;
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
            font-size: 1rem;
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
        
        
        /* GRİ - MOR TEMA */

.stApp {
    background:
        radial-gradient(circle at top right, rgba(139, 92, 246, 0.12), transparent 32%),
        linear-gradient(180deg, #111827 0%, #0F172A 100%);
    color: #F9FAFB;
}

/* Ana içerik kartları */
div[data-testid="stMetric"],
.security-card {
    background: rgba(31, 41, 55, 0.88) !important;
    border: 1px solid #374151 !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22) !important;
}

.notice-card {
    background: #1F2937 !important;
    color: #F9FAFB !important;
    border: 1px solid #374151 !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22) !important;
}

.notice-card * {
    color: #F9FAFB !important;
}

/* Metrik değerleri */
div[data-testid="stMetricValue"] {
    color: #C4B5FD !important;
    font-weight: 800 !important;
}

/* Başlıklar */
h1, h2, h3 {
    color: #F9FAFB !important;
}

h2::after,
h3::after {
    background: #8B5CF6 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #161B28 !important;
    border-right: 1px solid #374151 !important;
}

/* Butonlar */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(135deg, #7C3AED, #8B5CF6) !important;
    color: #FFFFFF !important;
    border: 1px solid #A78BFA !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #8B5CF6, #A78BFA) !important;
    border-color: #C4B5FD !important;
}

/* Segmented control */
button[role="radio"] {
    background: #1F2937 !important;
    color: #D1D5DB !important;
    border-color: #374151 !important;
}

button[role="radio"][aria-checked="true"] {
    background: #7C3AED !important;
    color: #FFFFFF !important;
}

/* Input alanları */
input,
textarea,
div[data-baseweb="select"] > div {
    background: #1F2937 !important;
    color: #F9FAFB !important;
    border-color: #4B5563 !important;
}

/* Dataframe çevresi */
div[data-testid="stDataFrame"] {
    border: 1px solid #374151 !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* Expander */
details {
    background: #1F2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 12px !important;
}

/* Bilgi kutuları */
div[data-testid="stAlert"] {
    background: rgba(31, 41, 55, 0.92) !important;
    color: #F9FAFB !important;
    border-left: 4px solid #8B5CF6 !important;
}

/* About kartı */

.about-card {
    background: #1F2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 16px !important;
    color: #F9FAFB !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.22) !important;
}

.about-card,
.about-card * {
    color: #F9FAFB !important;
}

.about-title {
    color: #C4B5FD !important;
    font-weight: 700;
}

.about-chip {
    background: #312E81 !important;
    color: #EDE9FE !important;
    border: 1px solid #8B5CF6 !important;
}


/* GLASSMORPHISM THEME */

:root {
    --glass-bg: rgba(31, 41, 55, 0.62);
    --glass-bg-strong: rgba(17, 24, 39, 0.78);
    --glass-border: rgba(196, 181, 253, 0.22);
    --glass-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
    --purple: #8B5CF6;
    --purple-light: #C4B5FD;
    --text-main: #F9FAFB;
    --text-soft: #D1D5DB;
}

/* Ana arka plan */
.stApp {
    background:
        radial-gradient(
            circle at 15% 10%,
            rgba(139, 92, 246, 0.18),
            transparent 28%
        ),
        radial-gradient(
            circle at 85% 18%,
            rgba(99, 102, 241, 0.14),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            #111827 0%,
            #0F172A 55%,
            #0B1120 100%
        ) !important;
}

/* Ana içerik genişliği */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

/* Ortak cam kart yapısı */
div[data-testid="stMetric"],
.notice-card,
.security-card,
.about-card,
div[data-testid="stAlert"],
details {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 18px !important;
    box-shadow: var(--glass-shadow) !important;
    backdrop-filter: blur(18px) saturate(140%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(140%) !important;
}

/* Metrik kartları */
div[data-testid="stMetric"] {
    padding: 1.15rem 1.25rem !important;
    min-height: 125px;
    transition:
        transform 0.2s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(167, 139, 250, 0.55) !important;
    box-shadow:
        0 22px 50px rgba(0, 0, 0, 0.34),
        0 0 26px rgba(139, 92, 246, 0.14) !important;
}

div[data-testid="stMetricLabel"] {
    color: var(--text-soft) !important;
    font-weight: 600 !important;
}

div[data-testid="stMetricValue"] {
    color: var(--purple-light) !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
}

/* Hero kartı */
.hero-card {
    position: relative;
    overflow: hidden;
    padding: 2rem 2.25rem !important;
    min-height: 190px;
    color: #F9FAFB !important;
    background:
        linear-gradient(
            135deg,
            rgba(139, 92, 246, 0.22),
            rgba(31, 41, 55, 0.58)
        ) !important;
    border: 1px solid rgba(196, 181, 253, 0.26) !important;
    border-radius: 22px !important;
    box-shadow:
        0 24px 60px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: blur(22px) saturate(145%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(145%) !important;
}

.hero-card::before {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    top: -110px;
    right: -80px;
    border-radius: 50%;
    background: rgba(167, 139, 250, 0.18);
    filter: blur(10px);
    pointer-events: none;
}

.hero-card h1,
.hero-card h2,
.hero-card h3,
.hero-card .hero-title {
    color: #FFFFFF !important;
    position: relative;
    z-index: 2;
}

.hero-card p,
.hero-card .hero-description {
    color: #D1D5DB !important;
    position: relative;
    z-index: 2;
    line-height: 1.7;
}

.hero-card strong {
    color: #EDE9FE !important;
}

/* Bilgi kartları */
.notice-card,
.security-card,
.about-card {
    padding: 1.25rem 1.35rem !important;
    color: var(--text-main) !important;
}

.notice-card *,
.security-card *,
.about-card * {
    color: inherit;
}

/* About kartı */
.about-title {
    color: var(--purple-light) !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}

.about-chip {
    display: inline-flex;
    align-items: center;
    background: rgba(76, 29, 149, 0.46) !important;
    color: #EDE9FE !important;
    border: 1px solid rgba(167, 139, 250, 0.38) !important;
    border-radius: 999px !important;
    padding: 0.38rem 0.7rem !important;
    margin: 0.2rem !important;
    backdrop-filter: blur(10px);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.84) !important;
    border-right: 1px solid rgba(196, 181, 253, 0.14) !important;
    backdrop-filter: blur(22px) saturate(140%) !important;
    -webkit-backdrop-filter: blur(22px) saturate(140%) !important;
}

/* Butonlar */
.stButton > button,
.stDownloadButton > button {
    background:
        linear-gradient(
            135deg,
            rgba(124, 58, 237, 0.96),
            rgba(139, 92, 246, 0.92)
        ) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(196, 181, 253, 0.42) !important;
    border-radius: 12px !important;
    box-shadow:
        0 10px 24px rgba(76, 29, 149, 0.28),
        inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
    font-weight: 700 !important;
    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        filter 0.18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.08);
    box-shadow:
        0 14px 30px rgba(76, 29, 149, 0.38),
        0 0 20px rgba(139, 92, 246, 0.18) !important;
}

/* Dosya yükleme alanı */
div[data-testid="stFileUploader"] {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 18px !important;
    padding: 0.65rem !important;
    box-shadow: var(--glass-shadow) !important;
    backdrop-filter: blur(18px) saturate(140%) !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: rgba(17, 24, 39, 0.5) !important;
    border: 1px dashed rgba(167, 139, 250, 0.5) !important;
    border-radius: 14px !important;
}

/* Input ve seçim alanları */
input,
textarea,
div[data-baseweb="select"] > div {
    background: rgba(17, 24, 39, 0.66) !important;
    color: var(--text-main) !important;
    border-color: rgba(196, 181, 253, 0.2) !important;
    backdrop-filter: blur(12px) !important;
}

/* DataFrame */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(196, 181, 253, 0.18) !important;
    border-radius: 16px !important;
    overflow: hidden;
    box-shadow: var(--glass-shadow) !important;
}

/* Başlıklar */
h1,
h2,
h3 {
    color: var(--text-main) !important;
    letter-spacing: -0.025em;
}

h1 {
    font-weight: 850 !important;
}

/* Segment kontrolü */
button[role="radio"] {
    background: rgba(31, 41, 55, 0.62) !important;
    color: var(--text-soft) !important;
    border-color: rgba(196, 181, 253, 0.18) !important;
    backdrop-filter: blur(12px) !important;
}

button[role="radio"][aria-checked="true"] {
    background:
        linear-gradient(
            135deg,
            rgba(124, 58, 237, 0.96),
            rgba(139, 92, 246, 0.9)
        ) !important;
    color: #FFFFFF !important;
}

/* Bölüm başlıkları */
.section-title,
.section-title *,
.section-heading,
.section-heading *,
[class*="section-title"],
[class*="section-title"] * {
    color: #F9FAFB !important;
}

/* Başlığın yanındaki numara/etiket */
.section-number,
.section-badge,
[class*="section-number"],
[class*="section-badge"] {
    color: #C4B5FD !important;
    background: rgba(76, 29, 149, 0.55) !important;
    border: 1px solid rgba(167, 139, 250, 0.35) !important;
}
@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.hero-card,
.notice-card,
.security-card,
.about-card,
div[data-testid="stMetric"]{
    animation: fadeUp .5s ease;
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