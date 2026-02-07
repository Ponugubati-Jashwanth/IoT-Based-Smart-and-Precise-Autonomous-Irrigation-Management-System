import requests
import pandas as pd
from datetime import datetime
import json
import random

# API setup
API_KEY = "your_openweather_api_key"  # Replace with your OpenWeather API key
locations = {
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Kandlakoya": {"lat": 17.5544, "lon": 78.4844},
    "Secunderabad": {"lat": 17.4399, "lon": 78.4983},
    "Gachibowli": {"lat": 17.4401, "lon": 78.3489},
    "Hitec City": {"lat": 17.4456, "lon": 78.3772},
    "Shamshabad": {"lat": 17.2403, "lon": 78.4294},
    "Medchal": {"lat": 17.6305, "lon": 78.4810},
    "Kukatpally": {"lat": 17.4849, "lon": 78.4138},
    "Madhapur": {"lat": 17.4486, "lon": 78.3908},
    "Banjara Hills": {"lat": 17.4156, "lon": 78.4347},
    "Jubilee Hills": {"lat": 17.4319, "lon": 78.4073},
    "Ameerpet": {"lat": 17.4374, "lon": 78.4487},
    "Begumpet": {"lat": 17.4447, "lon": 78.4664},
    "Uppal": {"lat": 17.4058, "lon": 78.5586},
    "LB Nagar": {"lat": 17.3457, "lon": 78.5477},
    "Dilsukhnagar": {"lat": 17.3687, "lon": 78.5242},
    "Miyapur": {"lat": 17.4969, "lon": 78.3517},
    "Kompally": {"lat": 17.5359, "lon": 78.4851},
    "Manikonda": {"lat": 17.4023, "lon": 78.3725},
    "Nizampet": {"lat": 17.5153, "lon": 78.3821},
    "Alwal": {"lat": 17.5016, "lon": 78.5201},
    "Malakpet": {"lat": 17.3725, "lon": 78.5112},
}

# Function to get weather data
def get_weather_data(lat, lon, place):
    if place in ["Hyderabad", "Kandlakoya"]:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        return response.json()
    else:
        # Simulate data for new locations
        return {
            "rain": {"1h": round(random.uniform(0, 8), 2)},
            "weather": [{"description": random.choice(["light rain", "moderate rain", "heavy rain", "drizzle", "clear sky", "scattered clouds", "overcast"])}]
        }

# Create a list to hold the data
data = []

# Fetch and store the data
for place, coords in locations.items():
    weather_data = get_weather_data(coords['lat'], coords['lon'], place)
    
    # Print weather data summary
    print(f"Weather data for {place}:")
    if place in ["Hyderabad", "Kandlakoya"]:
        print(json.dumps(weather_data, indent=2))
    else:
        print(f"  Simulated rainfall: {weather_data['rain']['1h']} mm")
        print(f"  Weather description: {weather_data['weather'][0]['description']}")
    
    timestamp = datetime.now()
    
    # Check for rain in both 'rain' and 'weather' fields
    rain_amount = weather_data.get("rain", {}).get("1h", 0)
    weather_description = weather_data.get("weather", [{}])[0].get("description", "")
    
    data.append({
        "Time": timestamp.strftime("%H:%M:%S"),
        "Date": timestamp.strftime("%Y-%m-%d"),
        "Place": place,
        "Rainfall (mm)": rain_amount,
        "Weather Description": weather_description
    })

# Create a DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel("rainfall_data.xlsx", index=False)

print("\nRainfall data has been saved to rainfall_data.xlsx")
print("\nDataFrame Summary:")
print(df)