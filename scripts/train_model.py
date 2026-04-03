"""
CENTENARYO ML Model Training Script
==================================

Purpose: Train Random Forest model for anomaly detection in senior citizen records
Connects to: backend/ml/random_forest_model.py, backend/database.py, backend/models.py
Dependencies: pandas, scikit-learn, sqlite3

This script handles the complete ML training pipeline for CENTENARYO:
- Loads historical senior citizen data from database
- Performs feature engineering for anomaly detection
- Trains Random Forest classifier on labeled data
- Evaluates model performance and accuracy
- Saves trained model for production use
- Generates feature importance reports

Training features include:
- Age distribution anomalies
- Registration pattern analysis
- Geographic clustering detection
- Benefit claim frequency analysis
- Demographic outlier detection

Usage:
    python scripts/train_model.py
    
Output:
- Trained model saved to backend/ml/models/
- Performance metrics and confusion matrix
- Feature importance analysis report

Used by: backend/ml/prescriptive_analytics.py for real-time anomaly detection
"""