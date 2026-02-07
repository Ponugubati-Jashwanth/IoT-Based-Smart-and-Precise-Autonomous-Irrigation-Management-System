import requests
import pandas as pd
from datetime import datetime

# API setup
API_KEY = "3f2eb7ed8de395280dc7e454fa80c174"  # Replace with your OpenWeather API key
locations = {
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Kandlakoya": {"lat": 17.5544, "lon": 78.4844},
}

# Function to get rainfall data
def get_rainfall_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    rain = data.get("rain", {}).get("1h", 0)  # Get rainfall for the past 1 hour, if available
    return rain

# Create a list to hold the data
data = []

# Fetch and store the data
for place, coords in locations.items():
    rainfall = get_rainfall_data(coords['lat'], coords['lon'])
    timestamp = datetime.now()
    data.append({
        "Time": timestamp.strftime("%H:%M:%S"),
        "Date": timestamp.strftime("%Y-%m-%d"),
        "Place": place,
        "Rainfall (mm)": rainfall
    })

# Create a DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel("rainfall_data.xlsx", index=False)

print("Rainfall data has been saved to rainfall_data.xlsx")
