"""
Data preprocessing module.
Handles encoding, scaling, and data transformation.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import Tuple, Dict, Any, List
from sklearn.preprocessing import StandardScaler, LabelEncoder

from ..utils.logger import ProjectLogger


class DataPreprocessor:
    """Preprocess data for model training."""
    
    def __init__(self, target_col: str = 'is_fraud'):
        """
        Initialize preprocessor.
        
        Args:
            target_col: Name of target variable column
        """
        self.target_col = target_col
        self.logger = ProjectLogger()
        
        # Preprocessing components
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler: StandardScaler = None
        
        # Feature lists (will be populated during fit)
        self.numeric_features: List[str] = []
        self.categorical_features: List[str] = []
        self.features_to_drop: List[str] = []
        
        self.logger.info("DataPreprocessor initialized")
    
    def identify_feature_types(self, df: pd.DataFrame) -> None:
        """Identify numeric and categorical features."""
        # Columns to always drop
        drop_cols = ['transaction_id', 'timestamp', self.target_col]
        self.features_to_drop = [col for col in drop_cols if col in df.columns]
        
        # Get remaining columns
        remaining_cols = [col for col in df.columns if col not in self.features_to_drop]
        
        # Identify types
        self.numeric_features = df[remaining_cols].select_dtypes(
            include=[np.number]
        ).columns.tolist()
        
        self.categorical_features = df[remaining_cols].select_dtypes(
            include=['object', 'category']
        ).columns.tolist()
        
        self.logger.info(f"Identified features: Numeric: {len(self.numeric_features)}, "
                        f"Categorical: {len(self.categorical_features)}, "
                        f"To drop: {len(self.features_to_drop)}")
    
    def encode_categorical_features(
        self, 
        df: pd.DataFrame,
        fit: bool = True
    ) -> pd.DataFrame:
        """
        Encode categorical features using Label Encoding.
        
        Args:
            df: Input DataFrame
            fit: Whether to fit encoders (True for train, False for test)
            
        Returns:
            DataFrame with encoded features
        """
        df_encoded = df.copy()
        
        for col in self.categorical_features:
            if col in df_encoded.columns:
                if fit:
                    self.label_encoders[col] = LabelEncoder()
                    df_encoded[col] = self.label_encoders[col].fit_transform(
                        df_encoded[col].astype(str)
                    )
                else:
                    if col in self.label_encoders:
                        # Handle unseen categories
                        le = self.label_encoders[col]
                        df_encoded[col] = df_encoded[col].astype(str).apply(
                            lambda x: le.transform([x])[0] if x in le.classes_ else -1
                        )
        
        print(f"✅ Encoded {len(self.categorical_features)} categorical features")
        return df_encoded
    
    def scale_numeric_features(
        self, 
        df: pd.DataFrame,
        fit: bool = True
    ) -> pd.DataFrame:
        """
        Scale numeric features using StandardScaler.
        
        Args:
            df: Input DataFrame
            fit: Whether to fit scaler (True for train, False for test)
            
        Returns:
            DataFrame with scaled features
        """
        df_scaled = df.copy()
        
        if fit:
            self.scaler = StandardScaler()
            df_scaled[self.numeric_features] = self.scaler.fit_transform(
                df_scaled[self.numeric_features]
            )
        else:
            if self.scaler:
                df_scaled[self.numeric_features] = self.scaler.transform(
                    df_scaled[self.numeric_features]
                )
        
        return df_scaled
    
    def fit_transform(
        self, 
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Fit and transform training data.
        
        Args:
            df: Input DataFrame with features and target
            
        Returns:
            Tuple of (X_processed, y)
        """
        # Identify feature types
        self.identify_feature_types(df)
        
        # Separate target
        if self.target_col in df.columns:
            y = df[self.target_col].copy()
            df_features = df.drop(columns=[self.target_col])
        else:
            y = None
            df_features = df.copy()
        
        # Drop unnecessary columns
        df_features = df_features.drop(columns=self.features_to_drop, errors='ignore')
        
        # Encode categorical features
        df_encoded = self.encode_categorical_features(df_features, fit=True)
        
        print(f"✅ Final feature matrix: {df_encoded.shape}")
        if y is not None:
            print(f"✅ Target vector: {y.shape}")
            print(f"Fraud rate: {y.mean():.2%}")
        
        # Scale numeric features
        df_scaled = self.scale_numeric_features(df_encoded, fit=True)
        
        print(f"✅ Scaled {len(self.numeric_features)} numeric features")
        
        return df_scaled, y
    
    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Transform new data using fitted preprocessor.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (X_processed, y)
        """
        # Separate target if present
        if self.target_col in df.columns:
            y = df[self.target_col].copy()
            df_features = df.drop(columns=[self.target_col])
        else:
            y = None
            df_features = df.copy()
        
        # Drop unnecessary columns
        df_features = df_features.drop(columns=self.features_to_drop, errors='ignore')
        
        # Encode categorical features
        df_encoded = self.encode_categorical_features(df_features, fit=False)
        
        # Scale numeric features
        df_scaled = self.scale_numeric_features(df_encoded, fit=False)
        
        return df_scaled, y
    
    def save_preprocessor(self, filepath: str = 'models/saved_models/preprocessor.pkl') -> None:
        """Save preprocessor to disk."""
        preprocessor_data = {
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'numeric_features': self.numeric_features,
            'categorical_features': self.categorical_features,
            'features_to_drop': self.features_to_drop
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(preprocessor_data, f)
        
        self.logger.info(f"💾 Preprocessor saved to: {filepath}")
    
    def load_preprocessor(self, filepath: str = 'models/saved_models/preprocessor.pkl') -> None:
        """Load preprocessor from disk."""
        with open(filepath, 'rb') as f:
            preprocessor_data = pickle.load(f)
        
        self.label_encoders = preprocessor_data['label_encoders']
        self.scaler = preprocessor_data['scaler']
        self.numeric_features = preprocessor_data['numeric_features']
        self.categorical_features = preprocessor_data['categorical_features']
        self.features_to_drop = preprocessor_data['features_to_drop']
        
        self.logger.info(f"✅ Preprocessor loaded from: {filepath}")

