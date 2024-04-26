import sqlite3
import pandas as pd
import joblib
import json

# Function to fetch data from the database
def fetch_data_from_database():
    conn = sqlite3.connect('iot_data.db')
    df = pd.read_sql_query("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 30", conn)
    conn.close()
    return df

# Function to run inference and predict the next 5 points
def predict_next_points():
    data = fetch_data_from_database()
    
    # Convert timestamp to datetime and set as index
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data.set_index('timestamp', inplace=True)
    
    # Load the trained models and scalers
    temperature_model = joblib.load('temperature_model.pkl')
    humidity_model = joblib.load('humidity_model.pkl')
    scaler = joblib.load('scaler.pkl')
    temperature_scaler = joblib.load('temperature_scaler.pkl')
    humidity_scaler = joblib.load('humidity_scaler.pkl')
    
    # Scale the input data
    data_scaled = scaler.transform(data)
    
    # Make predictions
    temperature_prediction = temperature_model.predict(data_scaled.reshape(1, -1))
    humidity_prediction = humidity_model.predict(data_scaled.reshape(1, -1))
    
    # Revert the scaling of the predictions
    temperature_prediction = temperature_scaler.inverse_transform(temperature_prediction.reshape(1, -1)).flatten()
    humidity_prediction = humidity_scaler.inverse_transform(humidity_prediction.reshape(1, -1)).flatten()
    
    # Convert predictions to list
    temperature_prediction = temperature_prediction.tolist()
    humidity_prediction = humidity_prediction.tolist()
    
    predictions = {
        'temperature': temperature_prediction,
        'humidity': humidity_prediction
    }
    
    return (json.dumps(predictions))

if __name__ == '__main__':
    predictions = predict_next_points()
    print(predictions)