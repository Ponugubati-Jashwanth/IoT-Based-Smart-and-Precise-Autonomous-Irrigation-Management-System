import requests
import time
import pandas as pd
import numpy as np
from datetime import datetime
import os
from flask import Flask, render_template_string, jsonify
from threading import Thread

# Telegram Bot details
TOKEN = "7759795188:AAGLarfdi5Co4E6iP7KxuBSVhNs_l3xeVeA"
CHAT_ID = "1948316604"

# ESP8266 server details
ESP8266_IP = "192.168.120.244"
ESP8266_PORT = "80"

# Excel file paths
log_file = "motor_log_small_field.xlsx"
field_file = "E:\\vscode\\python\\my_field.xlsx"

app = Flask(__name__)

# Global variables to store current readings
current_data = {
    "soil_moisture": 0,
    "temperature": 0,
    "humidity": 0,
    "motor_state": "OFF",
    "rainfall": 0
}

# Function to send messages to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Message sent to Telegram: {message}")
        else:
            print(f"Failed to send message: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error sending message: {e}")

# Function to get sensor data from ESP8266
def get_sensor_data():
    url = f"http://{ESP8266_IP}:{ESP8266_PORT}/get-data"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            soil_moisture = 1024 - data["soil_moisture"]
            temperature = data["temperature"]
            humidity = data["humidity"]
            return soil_moisture, temperature, humidity
        else:
            print(f"Failed to get sensor data: {response.status_code}")
            return None, None, None
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None, None, None

# Function to control the motor
def control_motor(state):
    url = f"http://{ESP8266_IP}:{ESP8266_PORT}/motor/{'on' if state else 'off'}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(response.text)
        else:
            print(f"Failed to control motor: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error: {e}")

# Function to get rainfall data from Excel
def get_rainfall_from_excel():
    df = pd.read_excel("E:\\vscode\\python\\rainfall_data.xlsx")
    rainfall_data = df[df['Place'] == 'Hyderabad'].tail(1)
    
    if not rainfall_data.empty:
        return rainfall_data['Rainfall (mm)'].values[0]
    else:
        return 0

# Function to extract field area and motor capacity from my_field.xlsx
def get_field_data():
    df = pd.read_excel(field_file, sheet_name='Field Data', skiprows=1)
    field_area = df['Field Area (acres)'].values[0]
    motor_capacity = df['Motor Pump Capacity (L/min)'].values[0]
    return field_area, motor_capacity

# Function to calculate motor run time for 5mm water
def calculate_motor_run_time(field_area, motor_capacity):
    mm_to_liters_per_sq_meter = 1.0
    acres_to_sq_meters = 4046.86
    total_water_needed = field_area * acres_to_sq_meters * mm_to_liters_per_sq_meter * 5
    motor_run_time = total_water_needed / motor_capacity
    return motor_run_time

# Function to calculate whether the motor should be on or off
def should_turn_on_motor(soil_moisture, temperature, humidity, rainfall):
    SM_threshold = 40
    T_ideal = 25
    H_ideal = 50
    a = 0.02
    b = 0.01
    c = 0.5
    adjustment_factor = 1 + a * (temperature - T_ideal) - b * (humidity - H_ideal) - c * rainfall
    return soil_moisture < SM_threshold * adjustment_factor

# Function to log motor status and inputs into an Excel file
def log_motor_status(motor_state, soil_moisture, temperature, humidity, rainfall, motor_run_time):
    columns = ["Date", "Time", "Soil Moisture", "Humidity (%)", "Rainfall (mm)", "Motor State", "Motor Run Time (min)"]
    
    if not os.path.exists(log_file):
        df = pd.DataFrame(columns=columns)
        df.to_excel(log_file, index=False)
        print("Excel file created with headers.")
    
    log_data = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Soil Moisture": soil_moisture,
        "Humidity (%)": humidity,
        "Rainfall (mm)": rainfall,
        "Motor State": "ON" if motor_state else "OFF",
        "Motor Run Time (min)": round(motor_run_time, 2) if motor_state else 0
    }
    
    df = pd.read_excel(log_file)
    new_row = pd.DataFrame([log_data])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    updated_df = updated_df[columns]
    updated_df.to_excel(log_file, index=False)
    
    print(f"Logged motor state: {log_data['Motor State']} with run time: {log_data['Motor Run Time (min)']} at {log_data['Time']}")
    send_telegram_message(f"Motor state: {log_data['Motor State']}, Run time: {log_data['Motor Run Time (min)']} min")

# Flask route for the web interface
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Irrigation System Monitor</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .reading { margin-bottom: 20px; }
            .chart-container { position: relative; height: 300px; width: 100%; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Irrigation System Monitor</h1>
            <div class="reading">
                <h2>Soil Moisture: <span id="soil-moisture"></span></h2>
            </div>
            <div class="reading">
                <h2>Temperature: <span id="temperature"></span>°C</h2>
            </div>
            <div class="reading">
                <h2>Humidity: <span id="humidity"></span>%</h2>
            </div>
            <div class="reading">
                <h2>Motor State: <span id="motor-state"></span></h2>
            </div>
            <div class="reading">
                <h2>Rainfall: <span id="rainfall"></span> mm</h2>
            </div>
            <div class="chart-container">
                <canvas id="myChart"></canvas>
            </div>
        </div>
        <script>
            const ctx = document.getElementById('myChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Soil Moisture',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            function updateReadings() {
                fetch('/get-data')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('soil-moisture').textContent = data.soil_moisture.toFixed(2);
                        document.getElementById('temperature').textContent = data.temperature.toFixed(2);
                        document.getElementById('humidity').textContent = data.humidity.toFixed(2);
                        document.getElementById('motor-state').textContent = data.motor_state;
                        document.getElementById('rainfall').textContent = data.rainfall.toFixed(2);

                        // Update chart
                        const now = new Date();
                        chart.data.labels.push(now.toLocaleTimeString());
                        chart.data.datasets[0].data.push(data.soil_moisture);
                        
                        if (chart.data.labels.length > 20) {
                            chart.data.labels.shift();
                            chart.data.datasets[0].data.shift();
                        }
                        
                        chart.update();
                    });
            }

            setInterval(updateReadings, 5000);
            updateReadings();
        </script>
    </body>
    </html>
    ''')

@app.route('/get-data')
def get_data():
    # Ensure all values are JSON serializable
    return jsonify({k: float(v) if isinstance(v, (np.integer, np.floating)) else v for k, v in current_data.items()})

def run_flask():
    app.run(host='0.0.0.0', port=5000)

def main_loop():
    last_motor_state = None

    while True:
        rainfall = get_rainfall_from_excel()
        soil_moisture, temperature, humidity = get_sensor_data()
        
        if soil_moisture is not None:
            field_area, motor_capacity = get_field_data()
            motor_run_time = calculate_motor_run_time(field_area, motor_capacity)
            motor_state = should_turn_on_motor(soil_moisture, temperature, humidity, rainfall)
            
            if motor_state != last_motor_state:
                control_motor(motor_state)
                log_motor_status(motor_state, soil_moisture, temperature, humidity, rainfall, motor_run_time)
                last_motor_state = motor_state
            
            # Update global current_data, converting NumPy types to Python types
            current_data["soil_moisture"] = float(soil_moisture)
            current_data["temperature"] = float(temperature)
            current_data["humidity"] = float(humidity)
            current_data["motor_state"] = "ON" if motor_state else "OFF"
            current_data["rainfall"] = float(rainfall)
        
        time.sleep(10)

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Run the main loop
    main_loop()
    #http://192.168.32.161:5000/