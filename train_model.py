import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
import joblib
import logging

# Configure logging
logging.basicConfig(filename='training.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Function to fetch data from the database
def fetch_data_from_database():
    conn = sqlite3.connect('iot_data.db')
    df = pd.read_sql_query("SELECT * FROM sensor_data", conn)
    conn.close()
    return df

# Function to create features and targets
def create_features_and_targets(data, data_scaled, num_history, num_future):
    X, y_temperature, y_humidity = [], [], []
    for i in range(len(data) - num_history - num_future + 1):
        X.append(data_scaled[i:i+num_history])
        y_temperature.append(data['temperature'][i+num_history:i+num_history+num_future])
        y_humidity.append(data['humidity'][i+num_history:i+num_history+num_future])
    return np.array(X), np.array(y_temperature), np.array(y_humidity)

# Function to train the models
def train_models():
    data = fetch_data_from_database()
    logging.info(f"Fetched {len(data)} rows of data from the database.")
    
    # Convert timestamp to datetime and set as index
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data.set_index('timestamp', inplace=True)

    # ffill the data
    data.fillna(method='ffill', inplace=True)
    
    # Normalize the features
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    num_history = 30
    num_future = 5
    X, y_temperature, y_humidity = create_features_and_targets(data, data_scaled, num_history, num_future)
    logging.info(f"Created features and targets with num_history={num_history} and num_future={num_future}.")
    
    # Reshape the input data and target data
    X = X.reshape(X.shape[0], -1)
    y_temperature = y_temperature.reshape(y_temperature.shape[0], -1)
    y_humidity = y_humidity.reshape(y_humidity.shape[0], -1)
    
    # Check for NaN and infinity values in target data
    nan_temp = np.isnan(y_temperature).any()
    inf_temp = np.isinf(y_temperature).any()
    nan_hum = np.isnan(y_humidity).any()
    inf_hum = np.isinf(y_humidity).any()
    
    if nan_temp or inf_temp:
        logging.warning("Temperature target data contains NaN or infinity values. Replacing with mean.")
        y_temperature = np.nan_to_num(y_temperature, nan=np.nanmean(y_temperature))
    
    if nan_hum or inf_hum:
        logging.warning("Humidity target data contains NaN or infinity values. Replacing with mean.")
        y_humidity = np.nan_to_num(y_humidity, nan=np.nanmean(y_humidity))
    
    # Scale the target values
    temperature_scaler = MinMaxScaler()
    y_temperature = temperature_scaler.fit_transform(y_temperature)
    
    humidity_scaler = MinMaxScaler()
    y_humidity = humidity_scaler.fit_transform(y_humidity)
    
    # Split the data into training and testing sets
    X_train, X_test, y_temperature_train, y_temperature_test, y_humidity_train, y_humidity_test = train_test_split(
        X, y_temperature, y_humidity, test_size=0.2, random_state=42, shuffle=False)
    logging.info(f"Split the data into training and testing sets. Training set size: {len(X_train)}, Testing set size: {len(X_test)}")
    
    # Create and train the XGBoost models
    temperature_model = XGBRegressor(objective='reg:squarederror', n_estimators=100)
    temperature_model.fit(X_train, y_temperature_train)
    logging.info("Trained the temperature model.")
    
    humidity_model = XGBRegressor(objective='reg:squarederror', n_estimators=100)
    humidity_model.fit(X_train, y_humidity_train)
    logging.info("Trained the humidity model.")
    
    # Evaluate the models
    temperature_pred = temperature_model.predict(X_test)
    humidity_pred = humidity_model.predict(X_test)
    
    # Revert the scaling of the predictions
    temperature_pred = temperature_scaler.inverse_transform(temperature_pred)
    humidity_pred = humidity_scaler.inverse_transform(humidity_pred)
    
    y_temperature_test = temperature_scaler.inverse_transform(y_temperature_test)
    y_humidity_test = humidity_scaler.inverse_transform(y_humidity_test)
    
    temperature_mse = mean_squared_error(y_temperature_test, temperature_pred)
    temperature_mae = mean_absolute_error(y_temperature_test, temperature_pred)
    temperature_r2 = r2_score(y_temperature_test, temperature_pred)
    
    humidity_mse = mean_squared_error(y_humidity_test, humidity_pred)
    humidity_mae = mean_absolute_error(y_humidity_test, humidity_pred)
    humidity_r2 = r2_score(y_humidity_test, humidity_pred)
    
    logging.info("Temperature Model Metrics:")
    logging.info(f"Mean Squared Error: {temperature_mse:.4f}")
    logging.info(f"Mean Absolute Error: {temperature_mae:.4f}")
    logging.info(f"R-squared: {temperature_r2:.4f}")
    
    logging.info("Humidity Model Metrics:")
    logging.info(f"Mean Squared Error: {humidity_mse:.4f}")
    logging.info(f"Mean Absolute Error: {humidity_mae:.4f}")
    logging.info(f"R-squared: {humidity_r2:.4f}")
    
    # Save the trained models and scalers
    joblib.dump(temperature_model, 'temperature_model.pkl')
    joblib.dump(humidity_model, 'humidity_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(temperature_scaler, 'temperature_scaler.pkl')
    joblib.dump(humidity_scaler, 'humidity_scaler.pkl')
    logging.info("Saved the trained models and scalers.")

if __name__ == '__main__':
    train_models()