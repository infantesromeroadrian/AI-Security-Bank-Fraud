"""
Data exploration module for EDA.
Comprehensive exploratory data analysis for fraud detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

from ..utils.logger import ProjectLogger


class DataExplorer:
    """Comprehensive EDA for fraud detection data."""
    
    def __init__(self, df: pd.DataFrame, target_col: str = 'is_fraud'):
        """
        Initialize data explorer.
        
        Args:
            df: Input DataFrame
            target_col: Name of target variable column
        """
        self.df = df.copy()
        self.target_col = target_col
        self.logger = ProjectLogger()
        
        # Identify feature types
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        self.datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Remove target from feature lists
        if target_col in self.numeric_cols:
            self.numeric_cols.remove(target_col)
        if target_col in self.categorical_cols:
            self.categorical_cols.remove(target_col)
        
        self.logger.info("DataExplorer initialized")
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive data summary."""
        self.logger.info("Generating data summary report...")
        
        report = {
            'shape': self.df.shape,
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024**2,
            'duplicates': self.df.duplicated().sum(),
            'numeric_features': len(self.numeric_cols),
            'categorical_features': len(self.categorical_cols),
            'datetime_features': len(self.datetime_cols),
            'missing_values': self.df.isnull().sum().sum(),
            'missing_features': self.df.isnull().sum()[self.df.isnull().sum() > 0].to_dict()
        }
        
        # Target variable analysis
        if self.target_col in self.df.columns:
            target_counts = self.df[self.target_col].value_counts()
            report['target_distribution'] = target_counts.to_dict()
            
            if len(target_counts) == 2:
                fraud_count = target_counts.get(1, 0)
                non_fraud_count = target_counts.get(0, 0)
                imbalance_ratio = non_fraud_count / fraud_count if fraud_count > 0 else 0
                report['imbalance_ratio'] = imbalance_ratio
        
        self.logger.info("Summary report generated successfully")
        return report
    
    def analyze_missing_values(self) -> pd.DataFrame:
        """Analyze missing values in dataset."""
        self.logger.info("Analyzing missing values...")
        
        missing = self.df.isnull().sum()
        missing_percent = (missing / len(self.df)) * 100
        
        missing_df = pd.DataFrame({
            'missing_count': missing,
            'missing_percent': missing_percent
        })
        
        missing_df = missing_df[missing_df['missing_count'] > 0].sort_values(
            by='missing_percent', ascending=False
        )
        
        if missing_df.empty:
            self.logger.info("✅ No missing values found!")
        else:
            self.logger.warning(f"Found {len(missing_df)} features with missing values")
        
        return missing_df
    
    def analyze_target_distribution(self) -> Dict[str, Any]:
        """Analyze target variable distribution."""
        self.logger.info(f"Analyzing target variable: {self.target_col}")
        
        if self.target_col not in self.df.columns:
            raise ValueError(f"Target column '{self.target_col}' not found")
        
        target_counts = self.df[self.target_col].value_counts()
        target_percent = (target_counts / len(self.df)) * 100
        
        analysis = {
            'counts': target_counts.to_dict(),
            'percentages': target_percent.to_dict()
        }
        
        # Calculate imbalance ratio for binary classification
        if len(target_counts) == 2:
            majority_class = target_counts.max()
            minority_class = target_counts.min()
            analysis['imbalance_ratio'] = majority_class / minority_class
        
        return analysis
    
    def analyze_numeric_features(self) -> pd.DataFrame:
        """Analyze numeric features statistics."""
        self.logger.info("Analyzing numeric features...")
        
        stats = self.df[self.numeric_cols].describe().T
        stats['missing'] = self.df[self.numeric_cols].isnull().sum()
        stats['unique'] = self.df[self.numeric_cols].nunique()
        stats['skewness'] = self.df[self.numeric_cols].skew()
        stats['kurtosis'] = self.df[self.numeric_cols].kurtosis()
        
        return stats
    
    def analyze_categorical_features(self) -> Dict[str, pd.Series]:
        """Analyze categorical features."""
        self.logger.info("Analyzing categorical features...")
        
        categorical_analysis = {}
        
        for col in self.categorical_cols:
            categorical_analysis[col] = {
                'unique_values': self.df[col].nunique(),
                'missing_values': self.df[col].isnull().sum(),
                'most_frequent': self.df[col].mode()[0] if not self.df[col].empty else None,
                'distribution': self.df[col].value_counts()
            }
        
        return categorical_analysis
    
    def detect_outliers(
        self, 
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> Dict[str, int]:
        """
        Detect outliers in numeric features.
        
        Args:
            method: Outlier detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            Dictionary with outlier counts per feature
        """
        self.logger.info(f"Detecting outliers using {method} method...")
        
        outliers = {}
        
        for col in self.numeric_cols:
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            
            elif method == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                outlier_mask = z_scores > threshold
            
            else:
                raise ValueError(f"Unknown method: {method}")
            
            outliers[col] = outlier_mask.sum()
        
        return outliers
    
    def correlation_analysis(self, method: str = 'pearson') -> pd.DataFrame:
        """
        Calculate correlation matrix for numeric features.
        
        Args:
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Correlation matrix DataFrame
        """
        self.logger.info(f"Computing {method} correlation matrix...")
        
        corr_matrix = self.df[self.numeric_cols].corr(method=method)
        return corr_matrix

