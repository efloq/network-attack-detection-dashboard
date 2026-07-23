"""Streamlit tabanlı ağ saldırısı tespit uygulaması."""

from __future__ import annotations

import logging

import streamlit as st

from csv_analyzer import render_csv_analysis_tab
from pcap_analyzer import render_pcap_analysis_tab
from ui import (
    configure_page,
    render_about,
    render_header,
    render_sidebar,
)


def configure_logging() -> None:
    """Sunucu tarafı log formatını yapılandırır."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    """Streamlit uygulamasını çalıştırır."""
    configure_logging()
    configure_page()
    render_sidebar()
    render_header()

    analysis_type = st.segmented_control(
        "Analiz Türü",
        options=["CSV Analizi", "PCAP Analizi"],
        default="CSV Analizi",
        selection_mode="single",
    )

    if analysis_type == "CSV Analizi":
        render_csv_analysis_tab()

    elif analysis_type == "PCAP Analizi":
        render_pcap_analysis_tab()

    render_about()


if __name__ == "__main__":
    main()