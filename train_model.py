import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_preprocess_data():
    try:
        # Check if dataset exists
        if not os.path.exists('data.csv'):
            logger.error("data.csv not found")
            raise FileNotFoundError("data.csv not found")
        
        logger.info("Loading dataset...")
        df = pd.read_csv('data.csv')
        
        # Map the actual columns to our required features
        df['num_credit_card'] = df['monthly_spend'] / 1000  # Approximate number of credit cards based on monthly spend
        df['num_of_loan'] = df['num_of_loans']
        df['num_of_delayed_payment'] = (df['payment_status'] == 'Delayed').astype(int)
        df['credit_utilization_ratio'] = (df['monthly_spend'] / df['annual_income']) * 100
        df['credit_history_age'] = df['credit_history']
        
        required_columns = [
            'annual_income',
            'num_credit_card',
            'num_of_loan',
            'num_of_delayed_payment',
            'credit_utilization_ratio',
            'credit_history_age',
            'credit_score'
        ]
        
        # Select features
        features = required_columns[:-1]
        X = df[features]
        y = df['credit_score']
        
        logger.info("Scaling features...")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        logger.info("Training model...")
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_scaled, y)
        
        logger.info("Saving model and scaler...")
        joblib.dump(rf_model, 'rf_model.joblib')
        joblib.dump(scaler, 'scaler.joblib')
        
        # Print model performance metrics
        from sklearn.metrics import mean_squared_error, r2_score
        y_pred = rf_model.predict(X_scaled)
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        logger.info(f"Model Performance:")
        logger.info(f"Mean Squared Error: {mse:.2f}")
        logger.info(f"R2 Score: {r2:.2f}")
        
        return rf_model, scaler
    except Exception as e:
        logger.error(f"Error in load_and_preprocess_data: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Starting model training...")
        rf_model, scaler = load_and_preprocess_data()
        logger.info("Model training completed successfully!")
    except Exception as e:
        logger.error(f"Failed to train model: {str(e)}")
        raise 