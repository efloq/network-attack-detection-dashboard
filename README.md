<div align="center">

# 🛡️ Network Attack Detection Dashboard

### Machine Learning & Flow-Based Network Traffic Analysis

A modern cybersecurity dashboard that combines **Machine Learning** and **Flow-Based Network Analysis** to detect suspicious network activities from CSV datasets and PCAP files.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.60-FF4B4B?logo=streamlit)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Random%20Forest-orange?logo=scikitlearn)
![NFStream](https://img.shields.io/badge/NFStream-Flow%20Analysis-purple)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

# 📌 Overview

Network Attack Detection Dashboard is a cybersecurity analysis platform developed during the **Microsoft AI Innovators Internship Program**.

The application provides two independent analysis modules:

- 🤖 **CSV Analysis** using a trained Random Forest model on the CICIDS2017 dataset.
- 🌐 **PCAP Analysis** using NFStream to extract network flows and perform rule-based security assessment.

The dashboard presents attack predictions, confidence scores, visual analytics and downloadable reports through an interactive Streamlit interface.

---

# ✨ Features

## 🤖 Machine Learning Analysis

- Random Forest attack detection
- CICIDS2017 support
- 77 network traffic features
- 15 attack classes
- Confidence Score
- Second Most Probable Class
- Risk Level Assessment
- Interactive charts
- CSV report export
- Missing / NaN / Infinite value validation

---

## 🌐 PCAP Flow Analysis

- NFStream flow extraction
- Protocol statistics
- Traffic visualization
- Top Talkers analysis
- Port analysis
- Rule-based security assessment
- Search & filtering
- Sortable flow table
- CSV report export

---

# 🖼️ Screenshots

## Dashboard

<img src="screenshots/dashboard.png" width="100%">

---

## CSV Analysis

<img src="screenshots/csv-analysis.png" width="100%">

---

## CSV Visual Analytics

<img src="screenshots/csv-visualization.png" width="100%">

---

## PCAP Flow Analysis

<img src="screenshots/pcap-analysis.png" width="100%">

---

# 🛠️ Technologies

| Category | Technologies |
|----------|--------------|
| Language | Python |
| Interface | Streamlit |
| Machine Learning | Scikit-learn |
| Model | Random Forest |
| Network Analysis | NFStream |
| Data Processing | Pandas |
| Visualization | Matplotlib |

---

# 📂 Project Structure

```text
network-attack-detection-dashboard
│
├── app.py
├── csv_analyzer.py
├── pcap_analyzer.py
├── ui.py
├── helpers.py
├── constants.py
├── network_attack_detector.pkl
├── label_encoder.pkl
├── requirements.txt
├── LICENSE
└── screenshots/
    ├── dashboard.png
    ├── csv-analysis.png
    ├── csv-visualization.png
    └── pcap-analysis.png
```

---

# 🚀 Installation

```bash
git clone https://github.com/efloq/network-attack-detection-dashboard.git

cd network-attack-detection-dashboard

python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

---

# 📊 Supported Files

| Analysis | Format |
|----------|--------|
| Machine Learning Analysis | `.csv` |
| Network Flow Analysis | `.pcap`, `.pcapng` |

---

# 👩‍💻 Developer

**Elifnur Sertkaya**

Microsoft AI Innovators Internship Project

---

# 📄 License

This project is licensed under the **MIT License**.