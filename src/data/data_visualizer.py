"""
Data visualization module.
Creates comprehensive visualizations for fraud detection analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Optional, Tuple

from ..utils.logger import ProjectLogger


class DataVisualizer:
    """Create visualizations for fraud detection data."""
    
    def __init__(self, df: pd.DataFrame, target_col: str = 'is_fraud'):
        """
        Initialize visualizer.
        
        Args:
            df: Input DataFrame
            target_col: Target variable column name
        """
        self.df = df.copy()
        self.target_col = target_col
        self.logger = ProjectLogger()
        
        # Identify feature types
        self.numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        if target_col in self.numeric_cols:
            self.numeric_cols.remove(target_col)
        if target_col in self.categorical_cols:
            self.categorical_cols.remove(target_col)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        self.logger.info("DataVisualizer initialized")
    
    def plot_target_distribution(self, figsize: Tuple[int, int] = (12, 5)) -> None:
        """Plot target variable distribution."""
        self.logger.info(f"Plotting {self.target_col} distribution...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Count plot
        target_counts = self.df[self.target_col].value_counts()
        ax1.bar(target_counts.index, target_counts.values, color=['#2ecc71', '#e74c3c'])
        ax1.set_xlabel(self.target_col.replace('_', ' ').title())
        ax1.set_ylabel('Count')
        ax1.set_title('Target Distribution (Counts)')
        ax1.set_xticks([0, 1])
        ax1.set_xticklabels(['Non-Fraud', 'Fraud'])
        
        # Add count labels
        for i, v in enumerate(target_counts.values):
            ax1.text(i, v + max(target_counts.values)*0.02, f'{v:,}', 
                    ha='center', fontsize=10, fontweight='bold')
        
        # Pie chart
        ax2.pie(target_counts.values, labels=['Non-Fraud', 'Fraud'],
               autopct='%1.2f%%', colors=['#2ecc71', '#e74c3c'],
               startangle=90, explode=[0, 0.1])
        ax2.set_title('Target Distribution (Percentage)')
        
        plt.tight_layout()
        plt.show()
        
        self.logger.info("✅ Target distribution plot created")
    
    def plot_numeric_distributions(
        self,
        cols: Optional[List[str]] = None,
        ncols: int = 3,
        figsize: Optional[Tuple[int, int]] = None
    ) -> None:
        """Plot distributions of numeric features."""
        if cols is None:
            cols = self.numeric_cols[:9]  # Limit to first 9
        
        nrows = (len(cols) + ncols - 1) // ncols
        if figsize is None:
            figsize = (ncols * 5, nrows * 4)
        
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        axes = axes.flatten() if nrows > 1 else [axes] if nrows == 1 else axes
        
        for idx, col in enumerate(cols):
            ax = axes[idx]
            self.df[col].hist(bins=50, ax=ax, color='skyblue', edgecolor='black')
            ax.set_title(f'{col}', fontsize=10, fontweight='bold')
            ax.set_xlabel('')
            ax.set_ylabel('Frequency')
            
        # Hide empty subplots
        for idx in range(len(cols), len(axes)):
            axes[idx].axis('off')
        
        plt.suptitle('Numeric Features Distribution', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        self.logger.info(f"✅ Plotted {len(cols)} numeric distributions")
    
    def plot_correlation_heatmap(
        self,
        figsize: Tuple[int, int] = (12, 10),
        method: str = 'pearson'
    ) -> None:
        """Plot correlation heatmap."""
        self.logger.info("Creating correlation heatmap...")
        
        corr_matrix = self.df[self.numeric_cols].corr(method=method)
        
        plt.figure(figsize=figsize)
        sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        plt.title(f'Feature Correlation Matrix ({method.title()})', 
                 fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        self.logger.info("✅ Correlation heatmap created")
    
    def plot_fraud_vs_nonfraud_comparison(
        self,
        cols: Optional[List[str]] = None,
        ncols: int = 3
    ) -> None:
        """Compare feature distributions for fraud vs non-fraud."""
        if cols is None:
            cols = self.numeric_cols[:6]
        
        nrows = (len(cols) + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*5, nrows*4))
        axes = axes.flatten() if nrows > 1 else [axes]
        
        for idx, col in enumerate(cols):
            ax = axes[idx]
            
            fraud_data = self.df[self.df[self.target_col] == 1][col]
            non_fraud_data = self.df[self.df[self.target_col] == 0][col]
            
            ax.hist([non_fraud_data, fraud_data], bins=30, label=['Non-Fraud', 'Fraud'],
                   color=['#2ecc71', '#e74c3c'], alpha=0.7, edgecolor='black')
            ax.set_title(f'{col}', fontweight='bold')
            ax.set_xlabel('')
            ax.set_ylabel('Frequency')
            ax.legend()
        
        # Hide empty subplots
        for idx in range(len(cols), len(axes)):
            axes[idx].axis('off')
        
        plt.suptitle('Fraud vs Non-Fraud Feature Comparison', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        self.logger.info("✅ Fraud comparison plots created")

