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
