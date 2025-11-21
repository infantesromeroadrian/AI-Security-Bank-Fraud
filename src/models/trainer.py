"""
Model training module with MLflow integration.
Trains multiple models and tracks experiments.
"""

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from typing import Dict, Any, Tuple, List
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    fbeta_score, roc_auc_score
)

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

import mlflow
import mlflow.sklearn

from ..utils.logger import ProjectLogger


class ModelTrainer:
    """Train ML models with MLflow tracking."""
    
    def __init__(self, experiment_name: str = "fraud_detection"):
        """
        Initialize model trainer.
        
        Args:
            experiment_name: MLflow experiment name
        """
        self.logger = ProjectLogger()
        self.experiment_name = experiment_name
        self.trained_models: Dict[str, Any] = {}
        self.model_results: Dict[str, Dict[str, float]] = {}
        
        # Setup MLflow
        mlflow.set_experiment(experiment_name)
        self.logger.info(f"ModelTrainer initialized with experiment: {experiment_name}")
    
    def train_model(
        self,
        model: Any,
        model_name: str,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        params: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """
        Train a single model with MLflow tracking.
        
        Args:
            model: Model instance to train
            model_name: Name for tracking
            X_train, y_train: Training data
            X_val, y_val: Validation data
            params: Model parameters to log
            
        Returns:
            Dictionary of validation metrics
        """
        with mlflow.start_run(run_name=model_name):
            self.logger.info(f"Training {model_name}...")
            
            # Log parameters
            if params:
                mlflow.log_params(params)
            
            # Train model
            model.fit(X_train, y_train)
            
            # Predict on validation set
            y_val_pred = model.predict(X_val)
            y_val_proba = model.predict_proba(X_val)[:, 1]
            
            # Calculate metrics
            metrics = {
                'precision': precision_score(y_val, y_val_pred, zero_division=0),
                'recall': recall_score(y_val, y_val_pred, zero_division=0),
                'f1_score': f1_score(y_val, y_val_pred),
                'f2_score': fbeta_score(y_val, y_val_pred, beta=2),
                'roc_auc': roc_auc_score(y_val, y_val_proba)
            }
            
            # Log metrics to MLflow
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Store results
            self.trained_models[model_name] = model
            self.model_results[model_name] = metrics
            
            self.logger.info(f"✅ {model_name} trained - Val F2: {metrics['f2_score']:.4f}, "
                           f"ROC-AUC: {metrics['roc_auc']:.4f}")
            
            return metrics
    
    def train_all_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series
    ) -> Tuple[Dict, Dict, str]:
        """
        Train all available models.
        
        Returns:
            Tuple of (trained_models, results, best_model_name)
        """
        self.logger.info("Starting multi-model training pipeline...")
        
        # 1. Logistic Regression (baseline)
        lr = LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            random_state=42
        )
        self.train_model(lr, 'Logistic_Regression', X_train, y_train, X_val, y_val,
                        params={'class_weight': 'balanced', 'max_iter': 1000})
        
        # 2. Random Forest
        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        self.train_model(rf, 'Random_Forest', X_train, y_train, X_val, y_val,
                        params={'n_estimators': 100, 'max_depth': 10, 'class_weight': 'balanced'})
        
        # 3. XGBoost (if available)
        if HAS_XGBOOST:
            scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
            xgb_model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                scale_pos_weight=scale_pos_weight,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
            self.train_model(xgb_model, 'XGBoost', X_train, y_train, X_val, y_val,
                            params={'n_estimators': 100, 'max_depth': 6, 'scale_pos_weight': float(scale_pos_weight)})
        
        # 4. LightGBM (if available)
        if HAS_LIGHTGBM:
            scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
            lgb_model = lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                scale_pos_weight=scale_pos_weight,
                random_state=42,
                verbose=-1
            )
            self.train_model(lgb_model, 'LightGBM', X_train, y_train, X_val, y_val,
                            params={'n_estimators': 100, 'max_depth': 6, 'scale_pos_weight': float(scale_pos_weight)})
        
        # Find best model based on F2-Score (prioritizes recall for fraud)
        best_model_name = max(self.model_results.keys(), 
                             key=lambda x: self.model_results[x]['f2_score'])
        
        self.logger.info(f"\n🏆 Best Model: {best_model_name} "
                        f"(F2-Score: {self.model_results[best_model_name]['f2_score']:.4f})")
        
        return self.trained_models, self.model_results, best_model_name
    
    def save_best_model(
        self,
        best_model_name: str,
        filepath: str = 'models/saved_models/best_model.pkl'
    ) -> None:
        """
        Save the best performing model.
        
        Args:
            best_model_name: Name of best model
            filepath: Path to save model
        """
        if best_model_name not in self.trained_models:
            raise ValueError(f"Model '{best_model_name}' not found in trained models")
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        best_model = self.trained_models[best_model_name]
        
        with open(filepath, 'wb') as f:
            pickle.dump(best_model, f)
        
        self.logger.info(f"💾 Best model ({best_model_name}) saved to: {filepath}")

