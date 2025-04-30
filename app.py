from flask import Flask, render_template, request, jsonify
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

app = Flask(__name__)


def load_and_preprocess_data():
    try:
        # Correct dataset name
        if not os.path.exists('data.csv'):
            logger.error("data.csv not found")
            raise FileNotFoundError("data.csv not found")
        
        logger.info("Loading dataset...")
        df = pd.read_csv('data.csv')  # <--- Fixed here
        
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
        
        return rf_model, scaler
    except Exception as e:
        logger.error(f"Error in load_and_preprocess_data: {str(e)}")
        raise

# Load model and scaler
try:
    logger.info("Loading model and scaler...")
    rf_model, scaler = load_and_preprocess_data()
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    raise

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        logger.info(f"Received prediction request with data: {data}")
        
        # Prepare input data directly from form
        input_data = np.array([
            data['annual_income'],
            data['num_credit_card'],
            data['num_of_loan'],
            data['num_of_delayed_payment'],
            data['credit_utilization_ratio'],
            data['credit_history_age']
        ]).reshape(1, -1)
        
        # Scale the input
        input_scaled = scaler.transform(input_data)
        
        # Get prediction
        final_score = int(rf_model.predict(input_scaled)[0])
        
        # Calculate score breakdown
        breakdown = {
            'payment_history': int(150 * (1 - data['num_of_delayed_payment'] / 12)),
            'credit_utilization': int(150 * (1 - data['credit_utilization_ratio'] / 100)),
            'credit_age': int(150 * (data['credit_history_age'] / 30))
        }
        
        # Determine rating and message
        if final_score >= 800:
            rating = "Excellent"
            message = "Outstanding! Keep up the great financial habits."
        elif final_score >= 740:
            rating = "Very Good"
            message = "Very good score! A little effort can make it excellent."
        elif final_score >= 670:
            rating = "Good"
            message = "You're doing well! Keep improving for an even better score."
        elif final_score >= 580:
            rating = "Fair"
            message = "You're on the right track. Focus on timely payments and lowering balances."
        else:
            rating = "Poor"
            message = "Don't worry — every expert was once a beginner. Improvement is very possible!"
        
        logger.info(f"Prediction successful. Score: {final_score}, Rating: {rating}")
        return jsonify({
            'score': final_score,
            'rating': rating,
            'breakdown': breakdown,
            'message': message
        })
        
    except Exception as e:
        error_msg = f"Error in prediction: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 400

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        data = request.get_json()
        logger.info(f"Received simulation request with data: {data}")
        
        if 'current_score' not in data or 'improvements' not in data:
            error_msg = "Missing required fields: current_score or improvements"
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 400
            
        current_score = data['current_score']
        improvements = data['improvements']
        
        improvement_factors = {
            'pay_bills_on_time': 0.1,
            'reduce_credit_utilization': 0.15,
            'avoid_new_credit': 0.05
        }
        
        total_improvement = 0
        improvements_made = []
        
        for action, selected in improvements.items():
            if selected:
                improvement = int(current_score * improvement_factors[action])
                total_improvement += improvement
                improvements_made.append(f"{action.replace('_', ' ').title()}: +{improvement} points")
        
        projected_score = min(current_score + total_improvement, 850)
        
        if projected_score >= 800:
            sim_message = "Amazing! You'll be among the top scorers."
        elif projected_score >= 740:
            sim_message = "You're moving into very strong territory!"
        elif projected_score >= 670:
            sim_message = "A little consistency will take you far."
        elif projected_score >= 580:
            sim_message = "Positive changes ahead — keep pushing!"
        else:
            sim_message = "Small steps lead to big wins. Stay committed!"

        logger.info(f"Simulation successful. Projected score: {projected_score}")
        return jsonify({
            'current_score': current_score,
            'projected_score': projected_score,
            'improvements_made': improvements_made,
            'sim_message': sim_message
        })
        
    except Exception as e:
        error_msg = f"Error in simulation: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 400

if __name__ == '__main__':
    app.run(debug=True)
