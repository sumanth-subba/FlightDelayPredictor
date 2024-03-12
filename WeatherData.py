import openmeteo_requests
import csv
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime

excel_file_path = 'weather_data.xlsx'
hourly_params = ["temperature_2m", "apparent_temperature", "rain", "wind_speed_10m", "wind_speed_100m", "cloud_cover", 
            "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "wind_direction_10m", "wind_direction_100m", "wind_gusts_10m",
            "snow_depth"]

def get_hourly_weather_df(longitude, latitude, time):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    #url = "https://api.open-meteo.com/v1/forecast"
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": hourly_params,
        "start_hour": time,
        "end_hour": time
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print("Getting weather response from API...")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    for i in range(len(hourly_params)):
        hourly_data[hourly_params[i]] = hourly.Variables(i).ValuesAsNumpy()

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_dataframe['date'] = hourly_dataframe['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return hourly_dataframe

def get_airport_long_lat(airport_code):
    print("Converting airport code to long & lat...")
    with open('iata-icao.csv', newline="", encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['iata'] == airport_code:
                return row['longitude'], row['latitude']
        return None, None
    
def convert_military_time(military_time, date):
    # get the year, month, date separately
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    year = date_obj.year
    month = date_obj.month
    day = date_obj.day

    # extract hour and minute
    hours = int(military_time[:2])
    minutes = int(military_time[2:])

    # round hour up
    if minutes > 30:
        hours += 1
    
    minutes = 0

    # create new date time
    date_time = datetime(year, month, day, hours, minutes)

    # format
    format_date_time = date_time.strftime("%Y-%m-%dT%H:%M")

    return format_date_time

def write_df_to_excel(hourly_dataframe):
    try:
        print("Writing to file...")
        exisiting_data = pd.read_excel(excel_file_path)
        combined_data = pd.concat([exisiting_data, hourly_dataframe], ignore_index=True)
    except FileNotFoundError:
        combined_data = hourly_dataframe

    combined_data.to_excel(excel_file_path, index=False)

def main():
    airport_code = "LGA"
    date = "2022-07-20"
    military_time = "1428"

    time = convert_military_time(military_time, date)
    
    long, lat = get_airport_long_lat(airport_code)
    
    if long is not None and lat is not None:
        df = get_hourly_weather_df(long, lat, time)
        write_df_to_excel(df)
    else:
        print("Could not find long & lat of this airport code, skipping...")

if __name__ == "__main__":
    main()

