"""
Complete training pipeline script.
Executes the full ML pipeline from data extraction to model saving.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.data_extractor import DataExtractor
from src.data.data_explorer import DataExplorer
from src.features.feature_engineer import FeatureEngineer
from src.features.preprocessor import DataPreprocessor
from src.data.data_splitter import DataSplitter
from src.models.trainer import ModelTrainer
import os
from dotenv import load_dotenv


def main():
    """Execute complete training pipeline."""
    
    # Load environment variables
    load_dotenv()
    
    print("="*70)
    print("BANK ANTI-FRAUD - TRAINING PIPELINE")
    print("="*70)
    
    # Phase 0: Data Extraction
    print("\n📥 PHASE 0: Data Extraction")
    extractor = DataExtractor(
        api_key=os.getenv('API_AIRTABLE', 'simulated'),
        base_id=os.getenv('AIRTABLE_BASE_ID'),
        table_name=os.getenv('AIRTABLE_TABLE_NAME', 'FraudBank')
    )
    
    # Try to load existing data, but validate it has required columns
    required_cols = ['amount', 'merchant_category', 'transaction_type', 'is_fraud']
    
    try:
        raw_data = extractor.extract_from_source(source_path='data/fraud_dataset.csv')
        
        # Validate columns
        missing_cols = [col for col in required_cols if col not in raw_data.columns]
        if missing_cols:
            print(f"⚠️  Local dataset missing required columns: {missing_cols}")
            print("🔄 Generating synthetic dataset with all required features...")
            raw_data = extractor._generate_synthetic_data(n_samples=10000)
    except Exception as e:
        print(f"⚠️  Error loading data: {e}")
        print("🔄 Generating synthetic dataset...")
        raw_data = extractor._generate_synthetic_data(n_samples=10000)
    
    extractor.save_raw_data(raw_data, filename='raw_fraud_transactions.csv')
    
    # Phase 1: EDA
    print("\n🔍 PHASE 1: Exploratory Data Analysis")
    explorer = DataExplorer(raw_data, target_col='is_fraud')
    summary = explorer.generate_summary_report()
    print(f"Dataset shape: {summary['shape']}")
    print(f"Fraud rate: {summary.get('imbalance_ratio', 'N/A')}")
    
    # Phase 3: Feature Engineering
    print("\n🔧 PHASE 3: Feature Engineering")
    engineer = FeatureEngineer()
    data_engineered = engineer.fit_transform(raw_data)
    print(f"Features after engineering: {len(data_engineered.columns)}")
    
    # Phase 3: Preprocessing
    print("\n⚙️  PHASE 3: Data Preprocessing")
    preprocessor = DataPreprocessor(target_col='is_fraud')
    X_processed, y = preprocessor.fit_transform(data_engineered)
    preprocessor.save_preprocessor('models/saved_models/fraud_preprocessor.pkl')
    
    # Phase 4: Data Split
    print("\n✂️  PHASE 4: Data Split & SMOTE")
    splitter = DataSplitter(test_size=0.2, val_size=0.2, random_state=42)
    splits = splitter.split_data(X_processed, y)
    
    # Apply SMOTE to training data
    X_train_balanced, y_train_balanced = splitter.apply_smote(
        splits['X_train'],
        splits['y_train'],
        sampling_strategy=0.3
    )
    splits['X_train'] = X_train_balanced
    splits['y_train'] = y_train_balanced
    
    splitter.save_splits(splits)
    
    # Phase 5: Model Training
    print("\n🤖 PHASE 5: Model Training")
    trainer = ModelTrainer(experiment_name='fraud_detection')
    trained_models, results, best_model_name = trainer.train_all_models(
        splits['X_train'],
        splits['y_train'],
        splits['X_val'],
        splits['y_val']
    )
    
    # Save best model
    trainer.save_best_model(best_model_name)
    
    print("\n" + "="*70)
    print("🎉 TRAINING PIPELINE COMPLETED!")
    print("="*70)
    print(f"\n🏆 Best Model: {best_model_name}")
    print(f"📊 F2-Score: {results[best_model_name]['f2_score']:.4f}")
    print(f"📊 ROC-AUC: {results[best_model_name]['roc_auc']:.4f}")
    print("\n💡 Next steps:")
    print("   1. Run API: uvicorn api.main:app --reload")
    print("   2. View MLflow: mlflow ui --port 5000")


if __name__ == "__main__":
    main()

