<div align="center">

# 🛡️ Intelligent Network Intrusion Detection & Risk Analysis System

### Machine Learning-Based Attack Classification & NFStream-Powered Flow Analysis

A modern cybersecurity dashboard that combines **Machine Learning** and **Flow-Based Network Analysis** to detect suspicious network activities from CSV datasets and PCAP files.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.60-FF4B4B?logo=streamlit)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Random%20Forest-orange?logo=scikitlearn)
![NFStream](https://img.shields.io/badge/NFStream-Flow%20Analysis-purple)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

# 📌 Overview

The **Intelligent Network Intrusion Detection & Risk Analysis System** is a cybersecurity analysis platform developed during the **Microsoft AI Innovators Internship Program**.

The system combines machine learning and flow-based traffic analysis to identify suspicious network activities and assess potential security risks.

It provides two complementary analysis modules:

- 🤖 **Machine Learning-Based CSV Analysis** using a trained Random Forest model on the CICIDS2017 dataset.
- 🌐 **Flow-Based PCAP Analysis** using NFStream to extract network flows and perform explainable rule-based security assessment.

The dashboard provides attack predictions, model probability scores, interactive visualizations and downloadable reports through an intuitive Streamlit interface.

---

# ✨ Features

> **Note:** The PCAP module performs **rule-based traffic assessment** and **does not** use machine learning classification.

## 🤖 Machine Learning Analysis

- Random Forest attack classification
- CICIDS2017 dataset support
- 77 network traffic features
- 15 attack classes
- Model Probability Score
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
| Programming Language | Python |
| User Interface | Streamlit |
| Machine Learning | Scikit-learn |
| Classification Model | Random Forest |
| Network Flow Analysis | NFStream |
| Data Processing | Pandas |
| Visualization | Matplotlib |

---

# 🏗️ System Architecture

```text
                    CSV FILE
                       │
                       ▼
             Feature Validation
                       │
                       ▼
               Random Forest Model
                       │
                       ▼
      Attack Classification & Risk Analysis
                       │
                       ▼
                  Streamlit Dashboard


                 PCAP / PCAPNG FILE
                       │
                       ▼
                    NFStream
                       │
                       ▼
               Flow Extraction
                       │
                       ▼
      Rule-Based Security Assessment
                       │
                       ▼
                  Streamlit Dashboard
```

---

# 📊 Model Performance

The Random Forest model was evaluated on a **stratified test set containing 462,762 network flows**.

### Overall Performance

| Metric | Score |
|--------|------:|
| Accuracy | **99.85%** |
| Macro Precision | **92.50%** |
| Macro Recall | **83.83%** |
| Macro F1-Score | **86.39%** |
| Weighted F1-Score | **99.85%** |

### Class-wise Performance

| Attack Type | Precision | Recall | F1-Score |
|-------------|----------:|-------:|---------:|
| Benign | 99.91% | 99.96% | 99.93% |
| Bot | 83.61% | 69.10% | 75.67% |
| DDoS | 99.98% | 99.94% | 99.96% |
| DoS Hulk | 99.82% | 99.54% | 99.68% |
| DoS Slowhttptest | 94.94% | 98.76% | 96.81% |
| DoS Slowloris | 99.63% | 99.07% | 99.35% |
| FTP-Patator | 99.92% | 99.33% | 99.62% |
| PortScan | 92.39% | 90.03% | 91.19% |
| SSH-Patator | 100.00% | 97.83% | 98.90% |
| Web Attack Brute Force | 74.67% | 77.21% | 75.92% |
| Web Attack XSS | 43.01% | 30.77% | 35.87% |

> **Note:** Rare attack classes such as **Heartbleed**, **SQL Injection**, and **Infiltration** contain very few samples. Therefore, their reported metrics should be interpreted cautiously.

---

# ⚠️ Dataset Limitations

The model was trained using the **CICIDS2017** dataset, which is highly imbalanced. While common attack categories contain hundreds of thousands of samples, several attack classes contain only a handful of instances.

Because of this imbalance:

- Accuracy alone is not sufficient to evaluate model performance.
- Macro F1-Score is reported alongside Accuracy and Weighted F1-Score.
- Minority attack classes may have lower recall despite the high overall accuracy.

The PCAP analysis module performs **rule-based traffic assessment** and **does not** classify attack types using machine learning. Instead, it identifies suspicious network behaviors such as port scanning or unusually high TCP activity using heuristic rules derived from NFStream flow statistics.

---

# 📂 Project Structure

```text
intelligent-network-intrusion-detection-risk-analysis-system
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
├── notebooks/
│   └── Network_Attack_Detection_Training.ipynb
└── screenshots/
    ├── dashboard.png
    ├── csv-analysis.png
    ├── csv-visualization.png
    └── pcap-analysis.png
```

---

# 🚀 Installation

```bash
git clone https://github.com/efloq/intelligent-network-intrusion-detection-risk-analysis-system.git

cd intelligent-network-intrusion-detection-risk-analysis-system

python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

---

# 📊 Supported File Formats

| Module | Supported Format |
|--------|------------------|
| Machine Learning Analysis | `.csv` |
| Flow-Based Analysis | `.pcap`, `.pcapng` |

---

# 🚀 Future Improvements

- Real-time packet capture
- Threat intelligence integration (AbuseIPDB / VirusTotal)
- Automatic model calibration
- Unit and integration tests
- Live network monitoring
- Docker deployment
- REST API support
- User authentication
- Explainable AI (XAI) support

---

# 👩‍💻 Developer

**Elifnur Sertkaya**

Computer Engineering Student

Microsoft AI Innovators Internship Project

---

# 📄 License

This project is licensed under the **MIT License**.