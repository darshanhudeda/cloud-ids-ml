# 🛡️ CloudGuard — Cloud-Based Intrusion Detection System

![Python](https://img.shields.io/badge/Python-3.12-blue)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20S3%20%7C%20SNS-orange)
![ML](https://img.shields.io/badge/ML-Random%20Forest-green)
![Status](https://img.shields.io/badge/Status-Live%20Deployed-brightgreen)

A fully deployed, cloud-native Intrusion Detection System that uses Machine Learning to classify network traffic in real time and send instant email alerts when attacks are detected.

> **Live Demo:** API endpoint deployed on AWS Lambda — detects DoS, Probe, R2L, U2R attacks in real time via REST API with email alerting via Amazon SNS.

---

## 📌 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Dataset](#dataset)
- [Model Performance](#model-performance)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [How to Run](#how-to-run)
- [API Usage](#api-usage)
- [Technologies Used](#technologies-used)
- [Future Improvements](#future-improvements)

---

## Overview

Traditional rule-based IDS tools like Snort rely on fixed signatures — they miss new and evolving attacks. CloudGuard uses a **Random Forest classifier** trained on real network traffic data to detect attack patterns without needing predefined rules.

**What makes this different:**
- Trained on 125,973 real network traffic records
- Handles severe class imbalance using SMOTE
- Deployed serverlessly on AWS Lambda — scales automatically
- Real-time REST API accessible from anywhere
- Instant email alerts via Amazon SNS
- Interactive Streamlit dashboard for live demo

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Streamlit Dashboard                                   │
│        │                                                │
│        │ HTTP POST (41 features)                        │
│        ▼                                                │
│   API Gateway (REST endpoint)                           │
│        │                                                │
│        │ Triggers                                       │
│        ▼                                                │
│   AWS Lambda (ids-inference)                            │
│        │                                                │
│        ├──▶ Amazon S3 (loads model on cold start)       │
│        │       rf_model.pkl                             │
│        │       scaler.pkl                               │
│        │       label_encoder.pkl                        │
│        │                                                │
│        ├──▶ ML Inference (Random Forest)                │
│        │       → Normal / DoS / Probe / R2L / U2R       │
│        │                                                │
│        ├──▶ Amazon SNS (if attack detected)             │
│        │       → Email Alert fired instantly            │
│        │                                                │
│        └──▶ JSON Response                               │
│               { prediction, confidence, alert }         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Features

- ✅ **5-class classification** — Normal, DoS, Probe, R2L, U2R
- ✅ **SMOTE oversampling** — fixes severe class imbalance (U2R: 52 → 67,343 samples)
- ✅ **Serverless deployment** — AWS Lambda, zero server management
- ✅ **Public REST API** — via Amazon API Gateway
- ✅ **Real-time email alerts** — via Amazon SNS
- ✅ **Two-layer alert system** — explicit classification + uncertainty-based flagging (confidence < 60%)
- ✅ **Interactive dashboard** — Streamlit UI with live traffic log
- ✅ **Traffic simulator** — auto-sends 20 mixed records for demo

---

## Dataset

**NSL-KDD** — Canadian Institute for Cybersecurity

| Split | Records | Features |
|-------|---------|----------|
| Train | 125,973 | 41 |
| Test  | 22,544  | 41 |

**Attack Categories:**

| Category | Description | Train Samples |
|----------|-------------|---------------|
| Normal | Legitimate traffic | 67,343 |
| DoS | Denial of Service | 45,927 |
| Probe | Port scanning | 11,656 |
| R2L | Remote to Local | 995 |
| U2R | User to Root | 52 |

Download: [Kaggle — NSL-KDD Dataset](https://www.kaggle.com/datasets/hassan06/nslkdd)

---

## Model Performance

**Random Forest Classifier (100 trees, max_depth=20)**

| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| DoS | 0.96 | 0.77 | **0.85** |
| Probe | 0.85 | 0.71 | **0.77** |
| Normal | 0.65 | 0.97 | **0.78** |
| R2L | 0.92 | 0.02 | 0.04 |
| U2R | 0.46 | 0.09 | 0.15 |
| **Overall Accuracy** | | | **75%** |

> Note: R2L and U2R low recall is a known challenge with NSL-KDD test set — it's intentionally harder than training to simulate real-world conditions. Addressed via two-layer alerting (low confidence = suspicious flag).

---

## Project Structure

```
cloud-ids-ml/
│
├── notebooks/
│   └── cloudguard_full_pipeline.ipynb   ← Full Colab notebook (EDA → Training → Upload)
│
├── lambda/
│   └── lambda_function.py               ← Lambda inference + SNS alerting code
│
├── dashboard/
│   └── dashboard.py                     ← Streamlit dashboard code
│
├── data/
│   └── columns.txt                      ← 41 NSL-KDD feature names
│
├── model_artifacts/
│   └── .gitkeep                         ← Model files stored in S3 (not in repo)
│
├── requirements.txt                     ← Python dependencies
├── .gitignore                           ← Ignores model files, credentials
└── README.md                            ← This file
```

---

## Setup & Installation

### Prerequisites
- Python 3.12+
- AWS Account (Free Tier)
- Google Colab (for training)
- Kaggle Account (for dataset)

### 1. Clone the repo
```bash
git clone https://github.com/darshanhudeda/cloud-ids-ml.git
cd cloud-ids-ml
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up AWS credentials
Add to Google Colab Secrets:
```
AWS_ACCESS_KEY  → your IAM access key
AWS_SECRET_KEY  → your IAM secret key
```

### 4. Create S3 bucket
```bash
# In AWS Console → S3 → Create bucket
# Name: your-ids-project
# Region: us-east-1
```

---

## How to Run

### Train the model (Google Colab)
```
1. Open notebooks/cloudguard_full_pipeline.ipynb in Google Colab
2. Run the Master Startup Block (Cell 1)
3. Run all cells in order:
   → Data loading → EDA → Preprocessing → Training → Upload to S3
```

### Deploy to AWS Lambda
```
1. Run packaging cells in notebook → uploads lambda_slim.zip to S3
2. AWS Console → Lambda → Create function → ids-inference → Python 3.12
3. Upload from S3 → add Lambda Layer (scikit-learn, numpy, joblib)
4. Add environment variables: BUCKET_NAME, SNS_ARN
5. Add API Gateway trigger → copy endpoint URL
```

### Run the Dashboard
```python
# In Google Colab
!pip install streamlit pyngrok -q
!ngrok authtoken YOUR_TOKEN

import subprocess
from pyngrok import ngrok

proc = subprocess.Popen(['streamlit', 'run', 'dashboard.py',
                         '--server.port', '8501',
                         '--server.headless', 'true'])
public_url = ngrok.connect(8501)
print("Dashboard:", public_url)
```

---

## API Usage

**Endpoint:** `POST https://your-api-id.execute-api.us-east-1.amazonaws.com/default/ids-inference`

**Request:**
```json
{
  "features": [0, 1, 2, 0, 491, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 1, 0, 0, 150, 25, 0.17, 0.03, 0.17, 0, 0.05, 0, 0, 0]
}
```

**Response:**
```json
{
  "prediction": "normal",
  "confidence": 0.9238,
  "alert": false
}
```

**Example (Python):**
```python
import requests

API_URL = "your-api-url-here"

response = requests.post(API_URL, json={
    "features": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                 511,511,1,1,0,0,1,0,0,255,255,1,0,1,0,1,1,0,0]
})

print(response.json())
# {'prediction': 'DoS', 'confidence': 0.5433, 'alert': True}
```

---

## Technologies Used

| Category | Technology |
|----------|-----------|
| Machine Learning | Python, scikit-learn, Random Forest |
| Data Processing | Pandas, NumPy, SMOTE (imbalanced-learn) |
| Cloud Platform | Amazon Web Services (AWS) |
| Deployment | AWS Lambda, Amazon API Gateway |
| Storage | Amazon S3 |
| Alerting | Amazon SNS |
| Dashboard | Streamlit, ngrok |
| Development | Google Colab, Python 3.12 |
| Dataset | NSL-KDD (Canadian Institute for Cybersecurity) |

---

## Future Improvements

- [ ] Live traffic ingestion using Zeek/Suricata packet capture
- [ ] Upgrade to CICIDS2017 dataset for modern attack patterns
- [ ] LSTM model for sequential traffic pattern detection
- [ ] Autoencoder for zero-day anomaly detection
- [ ] AWS Kinesis for real-time streaming pipeline
- [ ] Historical analytics dashboard (attack trends, heatmaps)
- [ ] Automated model retraining pipeline (MLOps/CI-CD)
- [ ] Threat intelligence integration (AbuseIPDB, MITRE ATT&CK)
- [ ] Mobile push notifications via Firebase
- [ ] Permanent deployment via Streamlit Cloud

---

## Academic Context

This project connects to published research on **ensemble ML frameworks for API gateway threat detection in mobile banking architectures**. The CloudGuard system demonstrates practical implementation of concepts from that paper — specifically around class imbalance handling and multi-class attack classification.

---

## Author

**Darshan** — Cybersecurity Student  
GitHub: [@darshanhudeda](https://github.com/darshanhudeda)  
Institution: East Point College of Higher Education, Bengaluru

---

## Acknowledgements

- Dataset: [NSL-KDD — Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/nsl.html)
- Cloud: [Amazon Web Services](https://aws.amazon.com)
- ML: [scikit-learn](https://scikit-learn.org)

---

*Built as part of AI-Powered Solution Expo 2026 — East Point College of Higher Education*
