
"""
Fraud Detection Monitoring System
Tracks model performance, data drift, and system health
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class FraudMonitor:
    """Production monitoring system for fraud detection model."""
    
    def __init__(self, baseline_data_path: str = '../data/processed/X_processed.csv'):
        """Initialize monitor with baseline data."""
        self.baseline_data = pd.read_csv(baseline_data_path)
        self.predictions_log = []
        self.performance_log = []
        self.drift_log = []
        
        # Create logs directory
        Path('../logs/monitoring').mkdir(parents=True, exist_ok=True)
        
    def log_prediction(self, features: dict, prediction: int, probability: float, 
                      actual: int = None):
        """Log a prediction for monitoring."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'features': features,
            'prediction': prediction,
            'probability': probability,
            'actual': actual
        }
        self.predictions_log.append(log_entry)
        
        # Save to file periodically
        if len(self.predictions_log) % 100 == 0:
            self._save_predictions_log()
    
    def _save_predictions_log(self):
        """Save predictions log to file."""
        filepath = Path('../logs/monitoring/predictions_log.json')
        with open(filepath, 'w') as f:
            json.dump(self.predictions_log, f, indent=2)
    
    def detect_data_drift(self, new_data: pd.DataFrame, threshold: float = 0.05):
        """
        Detect data drift using Kolmogorov-Smirnov test.
        
        Args:
            new_data: Recent production data
            threshold: P-value threshold for drift detection
            
        Returns:
            Dictionary with drift detection results
        """
        drift_results = {
            'timestamp': datetime.now().isoformat(),
            'features_with_drift': [],
            'drift_detected': False
        }
        
        common_cols = list(set(self.baseline_data.columns) & set(new_data.columns))
        
        for col in common_cols:
            # KS test for numerical features
            try:
                baseline_vals = self.baseline_data[col].dropna()
                new_vals = new_data[col].dropna()
                
                if len(baseline_vals) > 0 and len(new_vals) > 0:
                    statistic, p_value = stats.ks_2samp(baseline_vals, new_vals)
                    
                    if p_value < threshold:
                        drift_results['features_with_drift'].append({
                            'feature': col,
                            'p_value': p_value,
                            'statistic': statistic
                        })
                        drift_results['drift_detected'] = True
            except:
                continue
        
        self.drift_log.append(drift_results)
        return drift_results
    
    def calculate_performance_metrics(self, predictions: list, actuals: list):
        """Calculate performance metrics from recent predictions."""
        from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'n_samples': len(predictions),
            'precision': precision_score(actuals, predictions, zero_division=0),
            'recall': recall_score(actuals, predictions, zero_division=0),
            'f1_score': f1_score(actuals, predictions, zero_division=0),
            'fraud_rate': np.mean(actuals)
        }
        
        self.performance_log.append(metrics)
        return metrics
    
    def check_for_alerts(self, performance_metrics: dict, 
                        min_precision: float = 0.2, 
                        min_recall: float = 0.7):
        """Check if alerts should be triggered."""
        alerts = []
        
        if performance_metrics['precision'] < min_precision:
            alerts.append({
                'severity': 'HIGH',
                'type': 'LOW_PRECISION',
                'message': f"Precision dropped to {performance_metrics['precision']:.4f}",
                'timestamp': datetime.now().isoformat()
            })
        
        if performance_metrics['recall'] < min_recall:
            alerts.append({
                'severity': 'CRITICAL',
                'type': 'LOW_RECALL',
                'message': f"Recall dropped to {performance_metrics['recall']:.4f}",
                'timestamp': datetime.now().isoformat()
            })
        
        if alerts:
            self._save_alerts(alerts)
        
        return alerts
    
    def _save_alerts(self, alerts: list):
        """Save alerts to file."""
        filepath = Path('../logs/monitoring/alerts.json')
        
        # Load existing alerts
        existing_alerts = []
        if filepath.exists():
            with open(filepath, 'r') as f:
                existing_alerts = json.load(f)
        
        # Append new alerts
        existing_alerts.extend(alerts)
        
        # Save
        with open(filepath, 'w') as f:
            json.dump(existing_alerts, f, indent=2)
        
        print(f"⚠️  {len(alerts)} alert(s) triggered!")
        for alert in alerts:
            print(f"   [{alert['severity']}] {alert['message']}")
    
    def generate_monitoring_report(self):
        """Generate comprehensive monitoring report."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_predictions': len(self.predictions_log),
            'performance_metrics': self.performance_log[-10:] if self.performance_log else [],
            'drift_detections': self.drift_log[-5:] if self.drift_log else [],
            'summary': {
                'avg_precision': np.mean([m['precision'] for m in self.performance_log]) if self.performance_log else 0,
                'avg_recall': np.mean([m['recall'] for m in self.performance_log]) if self.performance_log else 0,
                'drift_detected_count': sum([1 for d in self.drift_log if d['drift_detected']])
            }
        }
        
        # Save report
        filepath = Path('../logs/monitoring/monitoring_report.json')
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

# Example usage
if __name__ == "__main__":
    monitor = FraudMonitor()
    print("✅ Fraud monitoring system initialized")
    print("📊 Monitoring capabilities:")
    print("   - Prediction logging")
    print("   - Data drift detection")
    print("   - Performance tracking")
    print("   - Alert system")
