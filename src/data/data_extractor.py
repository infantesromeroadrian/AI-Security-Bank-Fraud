"""
Data extraction module for fraud detection system.
Handles data extraction from multiple sources: Airtable API, local CSV, and synthetic generation.
"""

import os
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime, timedelta

from ..utils.logger import ProjectLogger


class DataExtractor:
    """
    Extract fraud detection data from various sources.
    
    Priority:
    1. Real Airtable connection (if configured)
    2. Local CSV file
    3. Synthetic data generation (fallback)
    """
    
    def __init__(
        self, 
        api_key: str = "simulated_key",
        base_id: Optional[str] = None,
        table_name: str = "FraudBank"
    ):
        """
        Initialize data extractor.
        
        Args:
            api_key: Airtable API key
            base_id: Airtable base ID
            table_name: Airtable table name
        """
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.base_url = "https://api.airtable.com/v0"
        self.logger = ProjectLogger()
        
        self.logger.info("DataExtractor initialized")
        if base_id:
            self.logger.info(f"Configured for Airtable: Base ID: {base_id[:8]}..., Table: {table_name}")
        else:
            self.logger.info("No Base ID provided - will use local files or generate synthetic data")
    
    def _authenticate(self) -> bool:
        """Validate API authentication."""
        self.logger.info("Authenticating with API...")
        
        if self.api_key and self.api_key != "simulated_api_key" and not self.api_key.startswith('your_'):
            self.logger.info("✅ Authentication successful")
            return True
        
        self.logger.error("❌ Authentication failed or API key is default/placeholder.")
        return False
    
    def _validate_data(self, df: pd.DataFrame, min_rows: int = 50) -> Tuple[bool, str]:
        """
        Validate extracted data meets quality requirements.
        
        Args:
            df: DataFrame to validate
            min_rows: Minimum number of rows required
            
        Returns:
            Tuple of (is_valid, message)
        """
        if df is None or df.empty:
            return False, "Data is empty"
        
        if len(df) < min_rows:
            return False, f"Insufficient data: {len(df)} rows (minimum: {min_rows})"
        
        return True, f"Data validated: {len(df)} rows, {len(df.columns)} columns"
    
    def _fetch_from_airtable(self) -> pd.DataFrame:
        """Fetch data from Airtable API."""
        if not self.base_id:
            raise ValueError("Base ID not configured")
        
        self.logger.info("Attempting Airtable connection...")
        
        url = f"{self.base_url}/{self.base_id}/{self.table_name}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        all_records = []
        offset = None
        
        while True:
            params = {"pageSize": 100}
            if offset:
                params["offset"] = offset
            
            self.logger.info(f"Fetching data from Airtable: {self.table_name}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            records = data.get('records', [])
            all_records.extend([record['fields'] for record in records])
            
            offset = data.get('offset')
            if not offset:
                break
        
        df = pd.DataFrame(all_records)
        self.logger.info(f"✅ Fetched {len(df)} records from Airtable")
        return df
    
    def _generate_synthetic_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """Generate synthetic fraud detection data."""
        self.logger.info("Generating synthetic bank fraud data...")
        self.logger.info(f"Generating {n_samples} synthetic transactions...")
        
        np.random.seed(42)
        
        # Transaction IDs
        transaction_ids = [f"TXN_{str(i).zfill(6)}" for i in range(n_samples)]
        
        # Timestamps
        start_date = datetime(2023, 1, 1)
        timestamps = [start_date + timedelta(minutes=i*5) for i in range(n_samples)]
        
        # Transaction amounts (log-normal distribution)
        amounts = np.random.lognormal(mean=3.5, sigma=1.5, size=n_samples)
        amounts = np.clip(amounts, 0.15, 20000)
        
        # Merchant categories
        categories = np.random.choice(
            ['food', 'gas', 'retail', 'entertainment', 'travel', 'online'],
            size=n_samples,
            p=[0.17, 0.16, 0.17, 0.17, 0.17, 0.16]
        )
        
        # Card present
        card_present = np.random.choice([0, 1], size=n_samples, p=[0.3, 0.7])
        
        # Transaction type
        transaction_type = np.random.choice(
            ['purchase', 'withdrawal', 'refund'],
            size=n_samples,
            p=[0.85, 0.10, 0.05]
        )
        
        # Customer features
        customer_age = np.random.randint(18, 80, size=n_samples)
        customer_tenure_days = np.random.randint(30, 3650, size=n_samples)
        
        # Distance features
        distance_from_home = np.random.gamma(shape=2, scale=25, size=n_samples)
        distance_from_last = np.random.gamma(shape=2, scale=15, size=n_samples)
        time_since_last = np.random.gamma(shape=2, scale=60, size=n_samples)
        
        # Velocity features
        avg_amount_30d = amounts * np.random.uniform(0.3, 1.5, size=n_samples)
        num_trans_24h = np.random.poisson(lam=3, size=n_samples)
        num_trans_7d = np.random.poisson(lam=15, size=n_samples)
        
        # Fraud labels (0.3-0.5% fraud rate is realistic)
        fraud_rate = 0.0035
        is_fraud = np.random.choice([0, 1], size=n_samples, p=[1-fraud_rate, fraud_rate])
        
        # Create DataFrame
        df = pd.DataFrame({
            'transaction_id': transaction_ids,
            'timestamp': timestamps,
            'amount': amounts,
            'merchant_category': categories,
            'card_present': card_present,
            'transaction_type': transaction_type,
            'distance_from_home': distance_from_home,
            'distance_from_last_transaction': distance_from_last,
            'time_since_last_transaction': time_since_last,
            'customer_age': customer_age,
            'customer_tenure_days': customer_tenure_days,
            'avg_transaction_amount_30d': avg_amount_30d,
            'num_transactions_24h': num_trans_24h,
            'num_transactions_7d': num_trans_7d,
            'is_fraud': is_fraud
        })
        
        fraud_count = is_fraud.sum()
        fraud_percentage = (fraud_count / n_samples) * 100
        
        self.logger.info(f"Generated data shape: {df.shape}")
        self.logger.info(f"Fraud rate: {fraud_percentage:.2f}%")
        
        return df
    
    def extract_from_source(
        self, 
        source_path: Optional[str] = None,
        use_airtable: Optional[bool] = None
    ) -> pd.DataFrame:
        """
        Extract data from best available source.
        
        Args:
            source_path: Path to local CSV file
            use_airtable: Force Airtable usage (if None, auto-detect)
            
        Returns:
            DataFrame with extracted data
        """
        self.logger.info("="*60)
        self.logger.info("STARTING DATA EXTRACTION")
        self.logger.info("="*60)
        
        # Strategy 1: Try Airtable if configured and not explicitly disabled
        if use_airtable is not False and self.base_id:
            try:
                self.logger.info("🌐 Attempting to fetch data from Airtable...")
                if self._authenticate():
                    df = self._fetch_from_airtable()
                    is_valid, message = self._validate_data(df)
                    
                    if is_valid:
                        self.logger.info(f"✅ {message}")
                        return df
                    else:
                        self.logger.warning(f"Airtable data validation failed: {message}")
            except Exception as e:
                self.logger.warning(f"Airtable fetch failed: {str(e)}")
        
        # Strategy 2: Try local CSV file
        if source_path and Path(source_path).exists():
            try:
                self.logger.info(f"📂 Loading data from local file: {source_path}")
                df = pd.read_csv(source_path)
                is_valid, message = self._validate_data(df, min_rows=50)
                
                if is_valid:
                    self.logger.info(f"✅ {message}")
                    return df
                else:
                    self.logger.warning(f"Local file validation failed: {message}")
            except Exception as e:
                self.logger.warning(f"Local file load failed: {str(e)}")
        
        # Strategy 3: Generate synthetic data as fallback
        self.logger.info("🔄 Using synthetic data as fallback...")
        df = self._generate_synthetic_data(n_samples=10000)
        
        is_valid, message = self._validate_data(df)
        if is_valid:
            self.logger.info(f"✅ {message}")
            return df
        else:
            raise RuntimeError(f"Synthetic data generation failed: {message}")
    
    def save_raw_data(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Save extracted data to raw data directory.
        
        Args:
            df: DataFrame to save
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path where data was saved
        """
        output_dir = Path('data/raw')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'raw_fraud_transactions_{timestamp}.csv'
        
        output_path = output_dir / filename
        df.to_csv(output_path, index=False)
        
        self.logger.info(f"✅ Raw data saved to: {output_path}")
        return str(output_path)

