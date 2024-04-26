import board
import adafruit_dht
import json
import requests

DHT_pin = board.D4

def get_outside_temperature(latitude, longitude, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        return data["main"]["temp"]
    else:
        return None

def read_sensor_data():
    dht_device = adafruit_dht.DHT11(DHT_pin)

    try:
        outside_temperature = get_outside_temperature(59.925970, 10.724851, "e45cd89943cd2b634916599e8849a436")
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        return  temperature, humidity, outside_temperature
    except RuntimeError as error:
        print(error.args[0])
        return None, None

if __name__ == '__main__':
    humidity, temperature, outside_temperature = read_sensor_data()
    if humidity is not None and temperature is not None and outside_temperature is not None:
        sensor_data = {
            'humidity': humidity,
            'temperature': temperature,
            'outside_temperature': outside_temperature
        }
        print(json.dumps(sensor_data))