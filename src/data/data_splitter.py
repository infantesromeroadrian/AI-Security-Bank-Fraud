"""
Data splitting module.
Handles train/validation/test splits with stratification and SMOTE.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

from ..utils.logger import ProjectLogger


class DataSplitter:
    """Split data into train/validation/test sets."""
    
    def __init__(
        self,
        test_size: float = 0.2,
        val_size: float = 0.2,
        random_state: int = 42
    ):
        """
        Initialize data splitter.
        
        Args:
            test_size: Proportion for test set
            val_size: Proportion for validation set (from remaining data)
            random_state: Random seed for reproducibility
        """
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        self.logger = ProjectLogger()
        
        self.logger.info("DataSplitter initialized")
        self.logger.info(f"Split configuration: test={test_size}, val={val_size}, seed={random_state}")
    
    def split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Dict[str, pd.DataFrame]:
        """
        Split data into train/validation/test sets with stratification.
        
        Args:
            X: Features DataFrame
            y: Target Series
            
        Returns:
            Dictionary containing all splits
        """
        self.logger.info("Splitting data with stratification...")
        
        # First split: train+val vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            stratify=y,
            random_state=self.random_state
        )
        
        # Second split: train vs validation
        val_size_adjusted = self.val_size / (1 - self.test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size_adjusted,
            stratify=y_temp,
            random_state=self.random_state
        )
        
        splits = {
            'X_train': X_train,
            'X_val': X_val,
            'X_test': X_test,
            'y_train': y_train,
            'y_val': y_val,
            'y_test': y_test
        }
        
        self.logger.info(f"✅ Data split complete:")
        self.logger.info(f"   Train: {len(X_train)} samples")
        self.logger.info(f"   Validation: {len(X_val)} samples")
        self.logger.info(f"   Test: {len(X_test)} samples")
        
        return splits
    
    def apply_smote(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        sampling_strategy: float = 0.3
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Apply SMOTE to balance training data.
        
        Args:
            X_train: Training features
            y_train: Training labels
            sampling_strategy: Desired ratio of minority to majority class
            
        Returns:
            Balanced (X_train, y_train)
        """
        self.logger.info(f"Applying SMOTE with sampling strategy: {sampling_strategy}")
        
        # Original distribution
        original_fraud = y_train.sum()
        original_total = len(y_train)
        
        # Apply SMOTE
        smote = SMOTE(
            sampling_strategy=sampling_strategy,
            random_state=self.random_state
        )
        
        X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
        
        # Convert back to DataFrame/Series
        X_resampled = pd.DataFrame(X_resampled, columns=X_train.columns)
        y_resampled = pd.Series(y_resampled, name=y_train.name)
        
        # Log results
        new_fraud = y_resampled.sum()
        new_total = len(y_resampled)
        added_samples = new_fraud - original_fraud
        
        self.logger.info(f"✅ SMOTE applied:")
        self.logger.info(f"   Original: {original_total} samples ({original_fraud} fraud)")
        self.logger.info(f"   After SMOTE: {new_total} samples ({new_fraud} fraud)")
        self.logger.info(f"   Added {added_samples} synthetic fraud samples")
        
        return X_resampled, y_resampled
    
    def save_splits(
        self,
        splits: Dict[str, pd.DataFrame],
        output_dir: str = 'data/splits'
    ) -> None:
        """
        Save data splits to disk.
        
        Args:
            splits: Dictionary of DataFrames to save
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for name, data in splits.items():
            filepath = output_path / f'{name}.csv'
            data.to_csv(filepath, index=False)
        
        self.logger.info(f"💾 Data splits saved to: {output_dir}")
        self.logger.info(f"Files: {list(splits.keys())}")

