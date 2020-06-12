
from datetime import datetime, timedelta
from google.oauth2 import service_account

import pandas as pd
import numpy as np

import pandas_gbq

import requests
import pickle
import os


# Defualt variables
project_id = "epidemicmodels"
table_id   = "real_data.raw_content_tm"
credentials = service_account.Credentials.from_service_account_file('../gkeys/epidemicModels-1fc10954f61b.json')
LOGGING_FILE = "./logging.pickle"
DEFAULT_LOG = dict(country=list(), items=list())

# The country list 
country_list = [/// "CN", "IT", "BR"]


if __name__ == "__main__":
  
  if os.path.isfile(LOGGING_FILE):
    with open(LOGGING_FILE, "rb") as handle:
      log_data = pickle.load(handle)
  else:
    log_data = DEFAULT_LOG

  # Get the data for each country
  covid_api = 'https://corona-api.com/countries/'
  for country in country_list:
    # Request the country data
    data_json =  requests.get(covid_api + country).json()
    # Get the population info
    N = data_json['data']['population']
    # Get the timeline data
    tm_data = data_json['data']['timeline']
    
    # Create a dataframe with the timeline data
    df = pd.DataFrame(tm_data)
    df = df.sort_values('date').reset_index()
    # Create the time vector
    df['date'] = [datetime.fromisoformat(f) for f in df['date']]
    df = df.drop_duplicates(subset='date', keep = 'last')
    # Preparing the dataframe...
    first_date = df['date'].iloc[0]
    size_days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
    date_vec = [first_date + timedelta(days=k) for k in range(size_days)]
    new_df = pd.DataFrame(date_vec, columns=['date'])
    new_df = pd.merge(new_df, df, how='left', on='date')
    new_df = new_df.drop(columns= ['index', 'updated_at', 'is_in_progress'])
    # Interpolating the dataframe columns
    for col in new_df.columns[1:]:
      new_df[col] = new_df[col].interpolate(method='polynomial', order=1)
    df = new_df.dropna()

    # Check if it is Brazil and correct 
    # some of the last data values
    if country == "BR":
      df.iloc[135,:] = [df.iloc[135, 0]] + [None]*7
      df = df.interpolate(method ='linear', limit_direction ='forward')
      df = df.where(df.active != 0.0).dropna()

    # Create the upload dictionary
    upload_data = dict()
    for item in ["active", "recovered", "deaths", "confirmed"]:
      upload_data[item] = df[item].values
    
    # Ensure all numeric columns have
    # the same data type
    for col in df.columns.to_list():
      if col != "date":
        if df[col].dtype != np.float64:
          df[col] = df[col].astype(np.float64)
    # Creating the country column
    df["country"] = country
    
    # Upload the data to the cloud
    # Create the table id
    if country in log_data["country"]:  
      # Remove the already existing data
      index = log_data["country"].index(country)
      items_size = log_data["items"][index]
      df = df.iloc[items_size:]
      # Print the uploaded content info
      print(" UPDATING COUNTRY...")
      print(" Uploading datatable of {}".format(country))
      print("    The item size: {}".format(items_size))
      print("    Table shape: {}".format(df.shape))
      print("    Table contents: {}".format(df.columns.to_list()))
      print("    Table ct types: {}".format(df.dtypes.to_list()))
      print("Processing done... Upload to cloud: (y/n)")
      input_data = input()
      if input_data.upper() == "Y":
        # Update the logging index track
        log_data["items"][index] += df.shape[0]
        pandas_gbq.to_gbq(df, table_id, project_id=project_id, credentials=credentials, if_exists='append')
        print("Uploaded!")
    else:
      # Print the uploaded content info
      print(" NEW COUNTRY!!")
      print(" Uploading datatable of {}".format(country))
      print("    Table shape: {}".format(df.shape))
      print("    Table contents: {}".format(df.columns.to_list()))
      print("    Table ct types: {}".format(df.dtypes.to_list()))
      print("Processing done... Upload to cloud: (y/n)")
      input_data = input()
      if input_data.upper() == "Y":
        # Create the loggin index track
        log_data["country"].append(country)
        log_data["items"].append(df.shape[0])
        pandas_gbq.to_gbq(df, table_id, project_id=project_id, credentials=credentials, if_exists='append')
        print("Uploaded!")

  if input_data.upper() == "Y":
    with open(LOGGING_FILE, "wb") as handle:
      pickle.dump(log_data, handle)

  print("DONE!")