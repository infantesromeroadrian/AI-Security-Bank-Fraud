# Bank Fraud ML Project - Original Plan & Design Document

**Project:** Enterprise-grade Bank Fraud Detection System  
**Created:** November 21, 2025  
**Status:** ✅ Completed  
**Type:** End-to-End Machine Learning Project

---

## 📋 Project Overview

Complete enterprise ML project for bank fraud detection, built from scratch in a Jupyter notebook following industry best practices:

- **Modular Code**: OOP-based, atomic classes
- **Scalability**: Reusable in any project
- **Reproducibility**: Complete documentation and versioning
- **Enterprise Standards**: Following corporate best practices

---

## 🎯 Project Phases (8 Total)

### Phase 0: Data Extraction (Simulated Corporate Environment)

**Objective:** Extract data as if in a corporate environment

**Implementation:**
- **Source:** Airtable API (simulated corporate data source)
- **DataExtractor Class:**
  - API authentication
  - Rate limiting handling
  - Error handling
  - Data validation (minimum rows requirement)
  - Save to data lake (local CSV)

**Features:**
- Multi-source fallback (Airtable → Local CSV → Synthetic)
- Comprehensive logging
- Data quality validation
- Synthetic data generation (10,000 records) as emergency backup

**Deliverables:**
- ✅ `data_extractor.py` module
- ✅ `.env` configuration file
- ✅ Raw data in `data/raw/` directory

---

### Phase 1: Data Exploration (EDA)

**Objective:** Comprehensive exploratory data analysis

**Implementation:**
- **DataExplorer Class** with analysis methods:
  - Statistical summary (shape, memory, duplicates)
  - Missing values analysis
  - Data types identification
  - Target variable distribution
  - Class imbalance analysis (fraud rate: 0.35%)
  - Feature correlation analysis (Pearson/Spearman)
  - Temporal patterns detection
  - Outlier detection (IQR method)

**Key Findings:**
- Dataset: 10,000 transactions
- Features: 15 original
- Fraud rate: 0.35% (35 fraud cases)
- Class imbalance: 1:284.7 ratio
- No missing values
- High correlation between amount and fraud

**Deliverables:**
- ✅ `data_explorer.py` module
- ✅ EDA report with statistics
- ✅ Correlation matrices

---

### Phase 2: Visualization

**Objective:** Create insightful visualizations for stakeholders

**Implementation:**
- **DataVisualizer Class** with plotting methods:
  - Target distribution (count + percentage)
  - Numeric feature distributions (histograms)
  - Categorical feature distributions (bar plots)
  - Correlation heatmaps (Pearson/Spearman)
  - Fraud vs Non-Fraud comparison plots
  - Temporal patterns (time series)

**Visualizations Created:**
- Transaction amount distributions by fraud status
- Merchant category fraud patterns
- Temporal fraud trends
- Feature correlation analysis
- Distance patterns (from home/last transaction)

**Deliverables:**
- ✅ `data_visualizer.py` module
- ✅ Professional plots for presentations
- ✅ Interactive visualizations

---

### Phase 3: Feature Engineering & Processing

**Objective:** Build robust preprocessing pipeline

**Implementation:**

**FeatureEngineer Class:**
1. **Amount Features:**
   - `amount_log`: Log transformation
   - `amount_category`: Categorical bins (very_low, low, medium, high)
   - `amount_to_avg_ratio`: Ratio to average transaction

2. **Temporal Features:**
   - `hour`, `day_of_week`, `day_of_month`
   - `is_weekend`: Weekend flag
   - `time_of_day`: Night/Morning/Afternoon/Evening
   - `is_peak_hour`: Peak hours flag (8-10 AM, 5-7 PM)

3. **Velocity Features:**
   - `is_high_frequency_24h`: High frequency in 24h
   - `is_high_frequency_7d`: High frequency in 7 days
   - `time_since_last_cat`: Time categories since last transaction

4. **Distance Features:**
   - `distance_home_cat`: Distance categories from home
   - `is_far_from_home`: Far from home flag (>100 km)
   - `is_far_from_last`: Far from last transaction flag (>50 km)

5. **Risk Score:**
   - Composite score (0-7 range)
   - Combines: high amount, card not present, far from home, high frequency

**DataPreprocessor Class:**
- Label Encoding for categorical features
- StandardScaler for numeric features
- Feature type identification
- Save/load preprocessor state

**Results:**
- Original: 15 features
- After Engineering: 31 features
- Final (after preprocessing): 28 features
- All features scaled and encoded

**Deliverables:**
- ✅ `feature_engineer.py` module
- ✅ `preprocessor.py` module
- ✅ Saved preprocessor (`fraud_preprocessor.pkl`)
- ✅ Processed data in `data/processed/`

---

### Phase 4: Data Split

**Objective:** Proper train/validation/test split with stratification

**Implementation:**
- **DataSplitter Class:**
  - Stratified split maintaining fraud ratio
  - Split: 60% Train / 20% Validation / 20% Test
  - SMOTE for class balancing (sampling_strategy=0.3)
  - Random state: 42 (reproducibility)

**Results:**
- **Original Train:** 6,000 samples (20 fraud = 0.33%)
- **After SMOTE:** 7,774 samples (1,794 fraud = 23.07%)
- **Validation:** 2,000 samples (original imbalance)
- **Test:** 2,000 samples (original imbalance)
- **Added:** 1,774 synthetic fraud samples

**Strategy:**
- Stratification preserves fraud ratio
- SMOTE only on training set
- Validation/Test keep real distribution

**Deliverables:**
- ✅ `data_splitter.py` module
- ✅ Train/val/test splits in `data/splits/`
- ✅ Balanced training set with SMOTE

---

### Phase 5: Model Training & Tracking

**Objective:** Train multiple models with MLflow tracking

**Implementation:**
- **ModelTrainer Class** with MLflow integration
- **Models Trained:**
  1. **Logistic Regression** (baseline)
     - class_weight='balanced'
     - max_iter=1000
  
  2. **Random Forest**
     - n_estimators=100
     - max_depth=10
     - class_weight='balanced'
  
  3. **XGBoost**
     - n_estimators=100
     - max_depth=6
     - scale_pos_weight (calculated)
  
  4. **LightGBM** (optional)
     - n_estimators=100
     - scale_pos_weight (calculated)

**MLflow Integration:**
- Experiment: "fraud_detection"
- Logged: Parameters, Metrics, Models, Artifacts
- Metrics: Precision, Recall, F1, F2, ROC-AUC
- Best model selection based on F2-Score

**Results (Validation Set):**
- **Logistic Regression:** F2=0.4464, ROC-AUC=0.9930 ⭐ WINNER
- **Random Forest:** F2=0.3409, ROC-AUC=0.9925
- **XGBoost:** F2=0.3409, ROC-AUC=0.9933

**Deliverables:**
- ✅ `trainer.py` module
- ✅ Trained models in `models/saved_models/`
- ✅ Best model saved (`best_model.pkl`)
- ✅ MLflow experiments in `./mlruns/`

---

### Phase 6: Evaluation

**Objective:** Comprehensive model evaluation with business metrics

**Implementation:**
- Evaluate best model (Logistic Regression) on test set
- **Metrics for Imbalanced Classification:**
  - Precision, Recall, F1-Score, F2-Score
  - ROC-AUC, PR-AUC
  - Confusion Matrix
  - Classification Report

**Test Set Results:**
- **Precision:** 26.09%
- **Recall:** 85.71% ⭐ (6 out of 7 frauds detected)
- **F1-Score:** 0.4000
- **F2-Score:** 0.5882
- **ROC-AUC:** 0.9926
- **PR-AUC:** 0.2766

**Confusion Matrix:**
```
TN: 1,976  |  FP: 17
FN: 1      |  TP: 6
```

**Business Metrics:**
- **False Positives:** 17 × $10 = $170
- **False Negatives:** 1 × $1,000 = $1,000
- **Total Cost:** $1,170 (per 2,000 transactions)

**Interpretation:**
- ✅ Excellent recall (catches most frauds)
- ⚠️ Lower precision (some false alarms)
- ✅ Low business cost
- ✅ Trade-off acceptable for fraud detection

**Deliverables:**
- ✅ Complete evaluation metrics
- ✅ Business cost analysis
- ✅ Model ready for production

---

### Phase 7: Deployment (REST API)

**Objective:** Deploy model as production-ready FastAPI service

**Implementation:**
- **FastAPI Application:**
  - Framework: FastAPI with Pydantic validation
  - Port: 8000
  - Auto-reload enabled
  - Swagger docs at `/docs`

**Endpoints:**
1. `GET /` - API information
2. `GET /health` - Health check
3. `GET /model_info` - Model metadata
4. `POST /predict` - Single transaction prediction
5. `POST /predict_batch` - Batch predictions

**Features:**
- Real-time feature engineering
- Pydantic input validation
- Risk level classification (LOW/MEDIUM/HIGH)
- Comprehensive error handling
- Automatic model loading
- Response time: < 100ms

**Request Example:**
```json
{
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
}
```

**Response Example:**
```json
{
  "is_fraud": 0,
  "fraud_probability": 0.023,
  "risk_level": "LOW",
  "timestamp": "2025-11-21T18:00:00"
}
```

**Deliverables:**
- ✅ `api/main.py` - FastAPI application
- ✅ Swagger documentation
- ✅ Tested endpoints
- ✅ Production-ready deployment

---

### Phase 8: Monitoring

**Objective:** Full monitoring system for production model

**Implementation:**
- **FraudMonitor Class:**

1. **Prediction Logging:**
   - Log all predictions with features
   - Save to JSON every 100 predictions
   - Include actual labels when available

2. **Data Drift Detection:**
   - Kolmogorov-Smirnov (KS) test
   - Compare feature distributions
   - Threshold: p-value < 0.05
   - Alert on significant drift

3. **Performance Tracking:**
   - Calculate metrics over time
   - Track: Precision, Recall, F1, Fraud Rate
   - Store in performance log

4. **Alert System:**
   - Trigger alerts on performance degradation
   - Thresholds: min_precision=0.2, min_recall=0.7
   - Save alerts to JSON
   - Console notifications

5. **Monitoring Reports:**
   - Generate comprehensive reports
   - Last 10 performance metrics
   - Last 5 drift detections
   - Summary statistics

**Monitoring Metrics:**
- Daily fraud rate
- Model performance over time
- Feature drift scores
- Alert counts

**Deliverables:**
- ✅ `fraud_monitor.py` module
- ✅ Drift detection system
- ✅ Performance tracking
- ✅ Alert mechanisms
- ✅ Monitoring reports in `logs/monitoring/`

---

## 🏗️ Final Project Structure

```
Bank-AntiFraud/
├── src/                        # Source code modules
│   ├── data/                   # Data handling (4 modules)
│   │   ├── data_extractor.py  ✅ 400+ lines
│   │   ├── data_explorer.py   ✅ 250+ lines
│   │   ├── data_visualizer.py ✅ 200+ lines
│   │   └── data_splitter.py   ✅ 150+ lines
│   ├── features/               # Feature engineering (2 modules)
│   │   ├── feature_engineer.py ✅ 200+ lines
│   │   └── preprocessor.py     ✅ 250+ lines
│   ├── models/                 # Model training (1 module)
│   │   └── trainer.py          ✅ 250+ lines
│   └── utils/                  # Utilities (1 module)
│       └── logger.py           ✅ 80+ lines
├── api/                        # REST API
│   └── main.py                 ✅ 200+ lines
├── monitoring/                 # Production monitoring
│   └── fraud_monitor.py        ✅ 200+ lines
├── scripts/                    # Execution scripts
│   └── train_pipeline.py       ✅ 100+ lines
├── config/                     # Configuration
│   └── config.yaml             ✅ 80+ lines
├── data/                       # Data files
│   ├── raw/                    # Raw data
│   ├── processed/              # Processed features
│   └── splits/                 # Train/val/test
├── models/                     # Saved models
│   └── saved_models/
│       ├── best_model.pkl
│       └── fraud_preprocessor.pkl
├── logs/                       # Application logs
├── tests/                      # Unit tests (future)
├── historyMD/                  # Documentation archive
├── requirements.txt            ✅
├── setup.py                    ✅
├── .gitignore                  ✅
├── README.md                   ✅
├── PROJECT_SUMMARY.md          ✅
├── AIRTABLE_SETUP.md           ✅
├── HISTORY.md                  ✅
└── DOCS_INDEX.md               ✅
```

---

## 📊 Project Statistics

### Code Metrics
- **Jupyter Notebook:** 4,267 lines
- **Python Modules:** 2,500+ lines (13 files)
- **Documentation:** 37.5 KB (5 markdown files)
- **Total Project Lines:** 7,000+

### Features
- **Original Features:** 15
- **Engineered Features:** 16
- **Final Features:** 28 (after preprocessing)

### Models
- **Models Trained:** 4
- **Best Model:** Logistic Regression
- **Training Time:** 24 seconds
- **Complete Pipeline:** 37 seconds

### Performance
- **Test Recall:** 85.71%
- **ROC-AUC:** 0.9926
- **Business Cost:** $1,170 per 2,000 transactions
- **API Response:** < 100ms

---

## 🎯 Success Criteria (All Met ✅)

- ✅ Clean, modular, reusable code
- ✅ OOP and SOLID principles
- ✅ High-quality documentation
- ✅ Model performance: F2-Score > 0.40 ✅
- ✅ API response time < 100ms ✅
- ✅ Comprehensive monitoring system ✅
- ✅ Production-ready deployment package ✅

---

## 🛠️ Technical Stack

### Data Processing
- **Pandas:** 2.0.0+
- **NumPy:** 1.24.0+
- **Scipy:** 1.10.0+

### Machine Learning
- **Scikit-learn:** 1.3.0+
- **XGBoost:** 2.0.0+
- **LightGBM:** 4.0.0+ (optional)
- **Imbalanced-learn:** 0.11.0+

### Experiment Tracking
- **MLflow:** 2.8.0+

### API Framework
- **FastAPI:** 0.104.0+
- **Uvicorn:** 0.24.0+
- **Pydantic:** 2.0.0+

### Visualization
- **Matplotlib:** 3.7.0+
- **Seaborn:** 0.12.0+
- **Plotly:** 5.17.0+

### Data Sources
- **Requests:** 2.31.0+
- **Python-dotenv:** 1.0.0+

---

## 🚀 How to Run

### 1. Installation
```bash
cd Bank-AntiFraud
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

### 3. Run Complete Pipeline
```bash
python scripts/train_pipeline.py
```

### 4. Start API
```bash
uvicorn api.main:app --reload --port 8000
```

### 5. View MLflow Experiments
```bash
mlflow ui --port 5000
```

---

## 📈 Timeline

**Total Development Time:** 8 hours

- Phase 0: 30 minutes
- Phase 1-2: 45 minutes
- Phase 3: 1 hour
- Phase 4: 30 minutes
- Phase 5: 1 hour
- Phase 6: 30 minutes
- Phase 7: 1 hour
- Phase 8: 30 minutes
- Modularization: 2 hours

---

## 🎉 Key Achievements

1. ✅ **Complete 8-phase ML pipeline**
2. ✅ **4,000+ line notebook → 2,500+ line modular code**
3. ✅ **Production-ready REST API**
4. ✅ **MLflow experiment tracking**
5. ✅ **Data drift monitoring**
6. ✅ **85.71% fraud detection rate**
7. ✅ **Comprehensive documentation (37.5 KB)**
8. ✅ **Scalable OOP architecture**

---

## 🔜 Future Enhancements

1. **Testing:** Add pytest unit tests
2. **CI/CD:** GitHub Actions workflow
3. **Docker:** Containerize application
4. **Dashboard:** Streamlit monitoring interface
5. **Authentication:** JWT tokens for API
6. **Database:** PostgreSQL/MongoDB integration
7. **Async:** Async endpoints for scalability
8. **Model Registry:** MLflow model registry

---

## 📚 Documentation

All documentation available in `historyMD/`:
- `README.md` - Quick start guide
- `PROJECT_SUMMARY.md` - Technical details
- `AIRTABLE_SETUP.md` - Integration guide
- `HISTORY.md` - Complete project history
- `DOCS_INDEX.md` - Navigation index
- `bank-fraud-ml-project.plan.md` - This document

---

## ✅ Project Status

**STATUS:** 🎊 PRODUCTION READY 🎊

**Completed:** November 21, 2025  
**Version:** 1.0.0  
**Author:** AI Engineer Path  

---

**End of Project Plan**

