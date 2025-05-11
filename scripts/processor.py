
import pandas as pd
import requests

import typing as ta


RUN_START_LAT_LONG: ta.Dict[str, ta.Tuple[float, float]] = {
    "Dogpatch": (-122.387374, 37.750979),
    "IndiaBasin": (-122.371618, 37.738194),
    "MissionBay": (-122.387928, 37.779745),
    "Marina": (-122.437813, 37.805879), 
    "GoldenGatePark": (-122.454938, 37.771662), 
    "BernalHeights": (-122.411619, 37.740527),
}

WEATHER_PARAMETERS = ["temperature_2m", "wind_speed_10m"]

BASE_API = "https://api.open-meteo.com/v1/forecast?"

def fetch_weather_data() -> pd.DataFrame:
    weather_data_list = []

    for parameter in WEATHER_PARAMETERS: 
        for neighborhood, (longitude, latitude) in RUN_START_LAT_LONG.items():
            API_REQUEST = BASE_API + f"latitude={latitude}&longitude={longitude}&hourly={parameter}"

            response = requests.get(API_REQUEST, timeout=10)
            data = response.json()

            processed_df = clean_weather_data(data, neighborhood, parameter)
            weather_data_list.append(processed_df)

    df = pd.concat(weather_data_list)  
    pivoted_df = df.pivot_table(
        index=["neighborhood", "time", "date", "timezone", "latitude", "longitude"],
        columns="parameter",
        values="value"
    ).reset_index()

    return pivoted_df

def clean_weather_data(data: ta.Dict[str, ta.Any], neighborhood: str, parameter: str) -> pd.DataFrame:
    hourly_df = pd.DataFrame(data['hourly'])
    hourly_df['latitude'] = data['latitude']
    hourly_df['longitude'] = data['longitude']
    hourly_df['timezone'] = data['timezone']


    # don't over-write time?
    hourly_df['time'] = pd.to_datetime(hourly_df['time'])
    hourly_df['date'] = hourly_df['time'].dt.date
    hourly_df['time'] = hourly_df['time'].dt.time

    hourly_df['neighborhood'] = neighborhood
    hourly_df['parameter'] = parameter # Replace this with units
    hourly_df['value'] = hourly_df[parameter]

    return hourly_df
