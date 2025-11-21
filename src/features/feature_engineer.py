"""
Feature engineering module for fraud detection.
Creates advanced features from raw transaction data.
"""

import pandas as pd
import numpy as np
from typing import List

from ..utils.logger import ProjectLogger


class FeatureEngineer:
    """Create engineered features for fraud detection."""
    
    def __init__(self):
        """Initialize feature engineer."""
        self.logger = ProjectLogger()
        self.logger.info("FeatureEngineer initialized")
    
    def create_amount_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create amount-based features."""
        df = df.copy()
        
        # Log transformation
        df['amount_log'] = np.log1p(df['amount'])
        
        # Categorical bins
        df['amount_category'] = pd.cut(
            df['amount'],
            bins=[0, 50, 200, 1000, np.inf],
            labels=['very_low', 'low', 'medium', 'high']
        ).astype(str)
        
        # Ratio to average
        df['amount_to_avg_ratio'] = df['amount'] / (df['avg_transaction_amount_30d'] + 1e-5)
        
        return df
    
    def create_temporal_features(
        self, 
        df: pd.DataFrame,
        datetime_col: str = 'timestamp'
    ) -> pd.DataFrame:
        """Create time-based features."""
        df = df.copy()
        
        if datetime_col in df.columns:
            # Ensure datetime type
            if not pd.api.types.is_datetime64_any_dtype(df[datetime_col]):
                df[datetime_col] = pd.to_datetime(df[datetime_col])
            
            # Extract temporal features
            df['hour'] = df[datetime_col].dt.hour
            df['day_of_week'] = df[datetime_col].dt.dayofweek
            df['day_of_month'] = df[datetime_col].dt.day
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            
            # Time of day categories
            df['time_of_day'] = pd.cut(
                df['hour'],
                bins=[0, 6, 12, 18, 24],
                labels=['night', 'morning', 'afternoon', 'evening']
            ).astype(str)
            
            # Peak hours (8-10 AM, 5-7 PM)
            df['is_peak_hour'] = df['hour'].isin([8, 9, 10, 17, 18, 19]).astype(int)
        
        return df
    
    def create_velocity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create transaction velocity features."""
        df = df.copy()
        
        # High frequency flags
        df['is_high_frequency_24h'] = (df['num_transactions_24h'] > 5).astype(int)
        df['is_high_frequency_7d'] = (df['num_transactions_7d'] > 20).astype(int)
        
        # Time since last transaction categories
        df['time_since_last_cat'] = pd.cut(
            df['time_since_last_transaction'],
            bins=[0, 10, 60, 300, np.inf],
            labels=['recent', 'normal', 'long_gap', 'very_long']
        ).astype(str)
        
        return df
    
    def create_distance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create distance-based features."""
        df = df.copy()
        
        # Distance from home categories
        df['distance_home_cat'] = pd.cut(
            df['distance_from_home'],
            bins=[0, 10, 50, 200, np.inf],
            labels=['very_close', 'close', 'medium', 'far']
        ).astype(str)
        
        # Far from home flag
        df['is_far_from_home'] = (df['distance_from_home'] > 100).astype(int)
        
        # Far from last transaction flag
        df['is_far_from_last'] = (df['distance_from_last_transaction'] > 50).astype(int)
        
        return df
    
    def create_risk_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create composite risk score."""
        df = df.copy()
        
        # Composite risk score (0-7 range)
        df['risk_score'] = (
            (df['amount'] > 1000).astype(int) * 2 +  # High amount
            (df['card_present'] == 0).astype(int) +   # Card not present
            (df['distance_from_home'] > 100).astype(int) +  # Far from home
            (df['num_transactions_24h'] > 5).astype(int) +  # High frequency
            (df.get('is_weekend', 0) * 0.5).astype(int) +   # Weekend
            (df.get('is_peak_hour', 0) == 0).astype(int)    # Off-peak hours
        )
        
        return df
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all feature engineering transformations."""
        self.logger.info("Starting feature engineering pipeline...")
        
        # Track feature count
        initial_features = len(df.columns)
        
        # Apply all transformations
        self.logger.info("Creating amount-based features...")
        df = self.create_amount_features(df)
        
        self.logger.info("Creating temporal features...")
        df = self.create_temporal_features(df)
        
        self.logger.info("Creating velocity features...")
        df = self.create_velocity_features(df)
        
        self.logger.info("Creating distance features...")
        df = self.create_distance_features(df)
        
        self.logger.info("Creating risk score...")
        df = self.create_risk_score(df)
        
        # Log results
        final_features = len(df.columns)
        new_features = final_features - initial_features
        
        self.logger.info(f"Feature engineering completed. Created {new_features} new features")
        
        return df

