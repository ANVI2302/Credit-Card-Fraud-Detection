# 🛡️ FraudGuard AI
### Real-Time Credit Card Fraud Detection Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-RandomForest-orange?style=flat-square&logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=flat-square)

> A full-stack machine learning web app that detects fraudulent credit card transactions in real time — built as a first-year AIML student project.

🔗 **https://credit-card-fraud-detection-anvi23.streamlit.app/**

---

## 📸 Preview

<img width="1738" height="876" alt="image" src="https://github.com/user-attachments/assets/e269be72-6695-4592-9160-61e649307e13" />
<img width="1617" height="925" alt="image" src="https://github.com/user-attachments/assets/2a492a14-6c45-416c-a180-e96bc542a7a5" />


---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 Single Transaction Analysis | Input 8 transaction features and get instant fraud prediction with confidence score |
| 📊 Batch CSV Analysis | Upload any CSV with transaction data for bulk fraud detection |
| 📄 PDF Report Export | Download a styled analysis report for any single transaction |
| 🎯 Risk Gauge | Visual fraud probability meter from 0–100% |
| ⚠️ Smart Preprocessing | Auto-detects column aliases, handles nulls, coerces types |
| 📈 Model Metrics | Precision, Recall, F1-Score and ROC-AUC with plain-English tooltips |

---

## 🧠 Model Details

- **Algorithm:** Random Forest Classifier
- **Features:** 8 engineered transaction features
- **Training Data:** 8,000 synthetic transactions
- **Decision Threshold:** 0.50

| Metric | Score |
|--------|-------|
| Precision | 1.00 |
| Recall | 0.60 |
| F1-Score | 0.75 |
| ROC-AUC | 1.00 |

### Input Features

| Feature | Description |
|---|---|
| `amount` | Transaction amount in USD |
| `transaction_hour` | Hour of day (0–23) |
| `merchant_category` | Clothing / Electronics / Food / Grocery / Travel |
| `foreign_transaction` | 1 if transaction is foreign, else 0 |
| `location_mismatch` | 1 if cardholder location doesn't match, else 0 |
| `device_trust_score` | Device trust score (0–100) |
| `velocity_last_24h` | Number of transactions in last 24 hours |
| `cardholder_age` | Age of cardholder |

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/ANVI2302/Credit-Card-Fraud-Detection.git
cd Credit-Card-Fraud-Detection

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python -m streamlit run fraud_app.py
```

Make sure `fraud_model.pkl` and `scaler.pkl` are in the same directory.

---

## 📁 Project Structure

```
Credit-Card-Fraud-Detection/
│
├── fraud_app.py           # Main Streamlit application
├── fraud_detection.ipynb  # Model training notebook
├── fraud_model.pkl        # Trained Random Forest model
├── scaler.pkl             # Fitted StandardScaler
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit, Plotly, Custom CSS
- **ML:** Scikit-learn (Random Forest), Pandas, NumPy
- **PDF Generation:** ReportLab
- **Deployment:** Streamlit Community Cloud

---

## 🤖 Honest Note

This project was built with AI assistance . I used it to write better code than I could alone at this stage — but I made the design decisions, debugged the errors, and understood what was being built.

That's how I think students should use AI — as a learning tool, not a shortcut.

---

## 👤 Author

**Anvi Shah** — First Year AIML Student  
[GitHub](https://github.com/ANVI2302) ·

---

> ⚠️ *This project is for educational/demonstration purposes only. Not intended for production financial use.*
