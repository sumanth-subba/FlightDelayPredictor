import openmeteo_requests
import csv
import os
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime

output_file_path = 'Flight_Info_and_Weather_Data.csv'
flights_file_path = 'flights_sample_3m.csv'
hourly_params = ["temperature_2m", "apparent_temperature", "rain", "wind_speed_10m", "wind_speed_100m", "cloud_cover", 
            "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "wind_direction_10m", "wind_direction_100m", "wind_gusts_10m",
            "snow_depth"]

dep_headers = ["dep_temperature_2m", "dep_apparent_temperature", "dep_rain", "dep_wind_speed_10m", "dep_wind_speed_100m", "dep_cloud_cover", 
            "dep_cloud_cover_low", "dep_cloud_cover_mid", "dep_cloud_cover_high", "dep_wind_direction_10m", "dep_wind_direction_100m", "dep_wind_gusts_10m",
            "dep_snow_depth"]

dest_headers = ["dest_temperature_2m", "dest_apparent_temperature", "dest_rain", "dest_wind_speed_10m", "dest_wind_speed_100m", "dest_cloud_cover", 
            "dest_cloud_cover_low", "dest_cloud_cover_mid", "dest_cloud_cover_high", "dest_wind_direction_10m", "dest_wind_direction_100m", "dest_wind_gusts_10m",
            "dest_snow_depth"]

def get_hourly_weather_df(longitude, latitude, time, header_info):
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
        hourly_data[header_info[i]] = hourly.Variables(i).ValuesAsNumpy()

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
    military_time = military_time.rjust(4, '0')

    year = date_obj.year
    month = date_obj.month
    day = date_obj.day

    # extract hour and minute
    hours = int(military_time[:2])
    minutes = int(military_time[2:])

    # round hour up
    if minutes > 30 and hours < 23:
        hours += 1
    elif minutes > 30 and hours >= 23:
        hours = 0
    
    minutes = 0

    # create new date time
    date_time = datetime(year, month, day, hours, minutes)

    # format
    format_date_time = date_time.strftime("%Y-%m-%dT%H:%M")

    return format_date_time

def write_df_to_excel(data_frame):
    try:
        print("Writing to file...")
        exisiting_data = pd.read_excel(output_file_path)
        combined_data = pd.concat([exisiting_data, data_frame], ignore_index=True)
    except FileNotFoundError:
        combined_data = data_frame

    combined_data.to_excel(output_file_path, index=False)

def append_weather_to_flights(start_row, end_row): #zero indexed
    flights_df = pd.read_csv(flights_file_path)

    flights_sub = flights_df.iloc[start_row:end_row]

    for index, row in flights_sub.iterrows():
        fl_date = row['FL_DATE']
        origin = row['ORIGIN']
        crs_dep_time = row['CRS_DEP_TIME']

        dest = row['DEST']
        crs_arr_time = row['CRS_ARR_TIME']

        dep_time = convert_military_time(str(crs_dep_time), str(fl_date))
        arr_time = convert_military_time(str(crs_arr_time), str(fl_date))

        dep_long, dep_lat = get_airport_long_lat(origin)
        arr_long, arr_lat = get_airport_long_lat(dest)

        if dep_long is not None and dep_lat is not None:
            dep_hourly_weather_df = get_hourly_weather_df(dep_long, dep_lat, dep_time, dep_headers)
            arr_hourly_weather_df = get_hourly_weather_df(arr_long, arr_lat, arr_time, dest_headers)

            dep_hourly_weather_df.index = [0]
            arr_hourly_weather_df.index = [0]

            combined_row = pd.concat([flights_df.loc[[index]].reset_index(drop=True), dep_hourly_weather_df, arr_hourly_weather_df], axis=1)
        
            # write combined df to excel files
            with open(output_file_path, 'a', newline='') as file:
                file_size = os.stat(output_file_path).st_size
                is_empty = file_size <= 2
                combined_row.to_csv(file, index=False, header=is_empty)

def main():  
    append_weather_to_flights(10,20)

if __name__ == "__main__":
    main()

