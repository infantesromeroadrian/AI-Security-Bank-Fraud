# 🏦 Bank Anti-Fraud Detection System

Enterprise-grade fraud detection system using Machine Learning.

## 📊 Project Overview

Complete end-to-end ML system for detecting fraudulent bank transactions with:
- Real-time fraud detection API
- MLflow experiment tracking
- Production monitoring system
- Data drift detection
- Comprehensive evaluation metrics

## 🎯 Model Performance

- **Best Model**: Logistic Regression
- **Test Recall**: 85.71% (catches 6 out of 7 frauds)
- **ROC-AUC**: 0.9926
- **F2-Score**: 0.5882 (optimized for fraud detection)
- **Business Cost**: $1,170 per 2,000 transactions

## 🏗️ Project Structure

```
Bank-AntiFraud/
├── src/
│   ├── data/              # Data handling modules
│   │   ├── data_extractor.py
│   │   ├── data_explorer.py
│   │   ├── data_splitter.py
│   │   └── data_visualizer.py
│   ├── features/          # Feature engineering
│   │   ├── feature_engineer.py
│   │   └── preprocessor.py
│   ├── models/            # Model training
│   │   └── trainer.py
│   └── utils/             # Utilities
│       └── logger.py
├── api/                   # FastAPI application
│   └── main.py
├── monitoring/            # Monitoring system
│   └── fraud_monitor.py
├── models/                # Saved models
│   └── saved_models/
├── data/                  # Data files
│   ├── raw/
│   ├── processed/
│   └── splits/
├── tests/                 # Unit tests
├── config/                # Configuration
├── scripts/               # Utility scripts
└── logs/                  # Application logs

```

## 🚀 Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file:
```env
API_AIRTABLE=your_api_key
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_TABLE_NAME=FraudBank
MLFLOW_TRACKING_URI=./mlruns
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Run the API

```bash
cd Bank-AntiFraud
uvicorn api.main:app --reload --port 8000
```

Visit:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. View MLflow Experiments

```bash
mlflow ui --port 5000
```

Visit: http://localhost:5000

## 📡 API Usage

### Predict Single Transaction

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.0,
    "merchant_category": "online",
    "card_present": 0,
    "transaction_type": "purchase",
    "distance_from_home": 150.0,
    "distance_from_last_transaction": 50.0,
    "time_since_last_transaction": 10.0,
    "customer_age": 35,
    "customer_tenure_days": 1000,
    "avg_transaction_amount_30d": 100.0,
    "num_transactions_24h": 5,
    "num_transactions_7d": 20
  }'
```

Response:
```json
{
  "is_fraud": 0,
  "fraud_probability": 0.023,
  "risk_level": "LOW",
  "timestamp": "2025-11-21T18:00:00"
}
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## 📈 Monitoring

```python
from monitoring.fraud_monitor import FraudMonitor

# Initialize monitor
monitor = FraudMonitor()

# Log predictions
monitor.log_prediction(features, prediction, probability, actual)

# Detect data drift
drift_results = monitor.detect_data_drift(new_data)

# Calculate performance
metrics = monitor.calculate_performance_metrics(predictions, actuals)

# Generate report
report = monitor.generate_monitoring_report()
```

## 🛠️ Development

### Code Style
- PEP 8 compliant
- Type hints on all functions
- Comprehensive docstrings
- OOP and SOLID principles

### Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

## 📚 Documentation

Full documentation available in the notebook:
- `fraud_detection_enterprise.ipynb` - Complete implementation guide

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👥 Authors

AI Engineer Path - Enterprise ML Development

## 🙏 Acknowledgments

- Scikit-learn for ML algorithms
- MLflow for experiment tracking
- FastAPI for modern API framework
- Imbalanced-learn for SMOTE implementation

