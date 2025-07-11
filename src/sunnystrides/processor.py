import os
import smtplib
import typing as ta
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import requests

from sunnystrides.constants import BASE_API, RUN_START_LAT_LONG, WEATHER_PARAMETERS
from sunnystrides.helpers import format_running_times_for_email_template

RECEIVER = os.environ["RECEIVER"]
SENDER = os.environ["SENDER"]
KEYS = os.environ["SMTP_GMAIL_PASS"]


def fetch_weather_data() -> pd.DataFrame:
    weather_data_list = []

    for parameter in WEATHER_PARAMETERS:
        for neighborhood, (longitude, latitude) in RUN_START_LAT_LONG.items():
            API_REQUEST = (
                BASE_API
                + f"latitude={latitude}&longitude={longitude}&hourly={parameter}&timezone=GMT-7"
            )

            response = requests.get(API_REQUEST, timeout=10)
            data = response.json()

            processed_df = clean_weather_data(data, neighborhood, parameter)
            weather_data_list.append(processed_df)

    df = pd.concat(weather_data_list)
    pivoted_df = df.pivot_table(
        index=["neighborhood", "time", "timezone", "latitude", "longitude"],
        columns="parameter",
        values="value",
    ).reset_index()

    return pivoted_df


def clean_weather_data(
    data: ta.Dict[str, ta.Any], neighborhood: str, parameter: str
) -> pd.DataFrame:
    hourly_df = pd.DataFrame(data["hourly"])
    hourly_df["latitude"] = data["latitude"]
    hourly_df["longitude"] = data["longitude"]
    hourly_df["timezone"] = data["timezone"]
    hourly_df["time"] = pd.to_datetime(hourly_df["time"])
    hourly_df["neighborhood"] = neighborhood
    hourly_df["parameter"] = parameter
    hourly_df["value"] = hourly_df[parameter]

    return hourly_df


def find_best_weather(df: pd.DataFrame) -> pd.DataFrame:

    # Filter for times between 8 am to 11 am and 5 pm to 8 pm
    df["time"] = pd.to_datetime(df["time"])
    df = df[
        (df["time"].dt.hour >= 8) & (df["time"].dt.hour <= 11)
        | (df["time"].dt.hour >= 17) & (df["time"].dt.hour <= 20)
    ]

    # Filter for times when temperature is above 15 degrees C and wind speed is below 20 kmh
    df = df[(df["temperature_2m"] >= 15) & (df["wind_speed_10m"] <= 20)]

    return df


def clean_up_and_generate_html_email(df: pd.DataFrame) -> str:
    email_template = [
        "<html><body>",
        "<h3>Neighborhoods with Optimal Running Times (temp above 15 degrees, windspeed below 20 km/h)</h3>",
    ]

    neighbors = df["neighborhood"].unique()

    for neighbor in neighbors:
        df_filtered = df[df["neighborhood"] == neighbor]
        times = df_filtered["time"].tolist()
        html_body = format_running_times_for_email_template(times)
        email_template.append(f"<h3>{neighbor}</h3><ul>")
        email_template.append(html_body)
        email_template.append("</ul>")
    email_template.append("</body></html>")

    return "".join(email_template)


def send_email(df: pd.DataFrame) -> None:

    msg = MIMEMultipart("alternative")
    msg["subject"] = "Optimal running times for this week"
    msg["From"] = SENDER
    msg["To"] = RECEIVER

    html_content = clean_up_and_generate_html_email(df)
    body = MIMEText(html_content, "html")
    msg.attach(body)

    # Setup server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER, KEYS)
    server.send_message(msg)
    server.quit()


if __name__ == "__main__":
    weather_data = fetch_weather_data()
    best_weather_df = find_best_weather(weather_data)
    send_email(best_weather_df)
