
"""
Fraud Detection API - FastAPI Application
Production-ready REST API for fraud detection predictions
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="Enterprise API for real-time fraud detection",
    version="1.0.0"
)

# Get correct paths (relative to project root)
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'models' / 'saved_models' / 'best_model.pkl'
PREPROCESSOR_PATH = BASE_DIR / 'models' / 'saved_models' / 'fraud_preprocessor.pkl'

# Load model and preprocessor
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(PREPROCESSOR_PATH, 'rb') as f:
        preprocessor = pickle.load(f)
    print("✅ Model and preprocessor loaded successfully")
    print(f"   Model path: {MODEL_PATH}")
except Exception as e:
    print(f"⚠️  Error loading model: {e}")
    print(f"   Looking for: {MODEL_PATH}")
    model = None
    preprocessor = None

# Pydantic models for request/response
class Transaction(BaseModel):
    amount: float = Field(..., description="Transaction amount")
    merchant_category: str = Field(..., description="Merchant category")
    card_present: int = Field(..., ge=0, le=1, description="Card present (0=No, 1=Yes)")
    transaction_type: str = Field(..., description="Transaction type")
    distance_from_home: float = Field(..., ge=0, description="Distance from home")
    distance_from_last_transaction: float = Field(..., ge=0)
    time_since_last_transaction: float = Field(..., ge=0)
    customer_age: int = Field(..., ge=18, le=120)
    customer_tenure_days: int = Field(..., ge=0)
    avg_transaction_amount_30d: float = Field(..., ge=0)
    num_transactions_24h: int = Field(..., ge=0)
    num_transactions_7d: int = Field(..., ge=0)

class PredictionResponse(BaseModel):
    is_fraud: int
    fraud_probability: float
    risk_level: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Fraud Detection API",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "POST - Single prediction",
            "/predict_batch": "POST - Batch predictions",
            "/health": "GET - Health check",
            "/model_info": "GET - Model information"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model else "unhealthy",
        model_loaded=model is not None,
        timestamp=datetime.now().isoformat()
    )

@app.get("/model_info")
async def model_info():
    """Get model information"""
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": type(model).__name__,
        "status": "active",
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: Transaction):
    """Predict fraud for a single transaction"""
    if not model or not preprocessor:
        raise HTTPException(status_code=503, detail="Model not available")
    
    try:
        # Convert to DataFrame
        data = pd.DataFrame([transaction.dict()])
        
        # Add timestamp for feature engineering
        data['timestamp'] = datetime.now()
        
        # Apply feature engineering (same as training)
        # Amount features
        data['amount_log'] = np.log1p(data['amount'])
        data['amount_category'] = pd.cut(data['amount'], bins=[0, 50, 200, 1000, np.inf], 
                                        labels=['very_low', 'low', 'medium', 'high']).astype(str)
        data['amount_to_avg_ratio'] = data['amount'] / (data['avg_transaction_amount_30d'] + 1e-5)
        
        # Temporal features
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        data['day_of_month'] = data['timestamp'].dt.day
        data['is_weekend'] = (data['day_of_week'] >= 5).astype(int)
        data['time_of_day'] = pd.cut(data['hour'], bins=[0, 6, 12, 18, 24], 
                                     labels=['night', 'morning', 'afternoon', 'evening']).astype(str)
        data['is_peak_hour'] = data['hour'].isin([8, 9, 10, 17, 18, 19]).astype(int)
        
        # Velocity features
        data['is_high_frequency_24h'] = (data['num_transactions_24h'] > 5).astype(int)
        data['is_high_frequency_7d'] = (data['num_transactions_7d'] > 20).astype(int)
        data['time_since_last_cat'] = pd.cut(data['time_since_last_transaction'], 
                                             bins=[0, 10, 60, 300, np.inf],
                                             labels=['recent', 'normal', 'long_gap', 'very_long']).astype(str)
        
        # Distance features
        data['distance_home_cat'] = pd.cut(data['distance_from_home'], 
                                           bins=[0, 10, 50, 200, np.inf],
                                           labels=['very_close', 'close', 'medium', 'far']).astype(str)
        data['is_far_from_home'] = (data['distance_from_home'] > 100).astype(int)
        data['is_far_from_last'] = (data['distance_from_last_transaction'] > 50).astype(int)
        
        # Risk score (simplified version)
        data['risk_score'] = (
            (data['amount'] > 1000).astype(int) * 2 +
            (data['card_present'] == 0).astype(int) +
            (data['distance_from_home'] > 100).astype(int) +
            (data['num_transactions_24h'] > 5).astype(int)
        )
        
        # Drop timestamp before preprocessing
        data = data.drop(columns=['timestamp'])
        
        # Apply preprocessor components (loaded as dict)
        df_processed = data.copy()
        
        # Encode categorical features
        for col, encoder in preprocessor['label_encoders'].items():
            if col in df_processed.columns:
                df_processed[col] = df_processed[col].astype(str).apply(
                    lambda x: encoder.transform([x])[0] if x in encoder.classes_ else -1
                )
        
        # Drop unnecessary columns
        cols_to_drop = [col for col in preprocessor['features_to_drop'] if col in df_processed.columns]
        df_processed = df_processed.drop(columns=cols_to_drop, errors='ignore')
        
        # Scale numeric features
        numeric_cols = preprocessor['numeric_features']
        available_numeric = [col for col in numeric_cols if col in df_processed.columns]
        df_processed[available_numeric] = preprocessor['scaler'].transform(df_processed[available_numeric])
        
        # Make prediction
        prediction = model.predict(df_processed)[0]
        probability = model.predict_proba(df_processed)[0][1]
        
        # Determine risk level
        if probability >= 0.7:
            risk_level = "HIGH"
        elif probability >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return PredictionResponse(
            is_fraud=int(prediction),
            fraud_probability=float(probability),
            risk_level=risk_level,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict_batch")
async def predict_batch(transactions: List[Transaction]):
    """Predict fraud for multiple transactions"""
    if not model:
        raise HTTPException(status_code=503, detail="Model not available")
    
    results = []
    for transaction in transactions:
        try:
            result = await predict_fraud(transaction)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    
    return {
        "predictions": results,
        "total": len(transactions),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
