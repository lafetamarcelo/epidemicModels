from flask                import Flask, request, jsonify
from flask_restful        import Resource, Api
from flask_request_params import bind_request_params

from datetime import datetime, timedelta
from google.oauth2 import service_account

import pandas as pd
import numpy as np

import pandas_gbq

import requests
import pickle
import os

# Defualt variables
COUNTRY_LIST = ["BR", "IT", "CN", "DE"]

PROJECT_ID   = "epidemicapp-280600"
TABLE_ID     = "countries.real_data_test"
TABLE_LOG_ID = "countries.data_log_test"
LOG_QUERY    = "SELECT * FROM countries.data_log_test"

CREDENTIALS  = service_account.Credentials.from_service_account_file('./keys/epidemicapp-62d0d471b86f.json')
pandas_gbq.context.credentials = CREDENTIALS

DEFAULT_LOG  = dict(country=list(), items=list())


class real_data_trigger(Resource):
  def get(self):
    # Call the update all countries 
    # pipeline 
    # 
    update_all_countries_pipe()


def update_all_countries_pipe():
  """
  
  """
  # Check if logging file exists
  # if does not, create the logging
  # as default file
  
  try:
    # Reading the log table...
    log_df = pandas_gbq.read_gbq(LOG_QUERY, project_id=PROJECT_ID)
    country_list = log_df["country"].to_list()
    start_p_list = log_df["days_collected"].to_list()
    log_data = dict(country=country_list, items=start_p_list)
  except:
    print("Country log table does not yet, exist...")
    log_data = DEFAULT_LOG

  # Get the data for each country
  covid_api = 'https://corona-api.com/countries/'
  for country in COUNTRY_LIST:
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
      print(" UPDATING COUNTRY {}...".format(country))
      print(" Uploading datatable of {}".format(country))
      print("    The item size: {}".format(items_size))
      print("    Table shape: {}".format(df.shape))
      print("    Table contents: {}".format(df.columns.to_list()))
      print("    Table ct types: {}".format(df.dtypes.to_list()))
      try:
        # Update the logging index track
        log_data["items"][index] += df.shape[0]
        pandas_gbq.to_gbq(df, TABLE_ID, project_id=PROJECT_ID, credentials=CREDENTIALS, if_exists='append')
        print("Uploaded!")
      except Exception as e:
        print("Error on uploading {}...".format(e))
    else:
      # Print the uploaded content info
      print(" NEW COUNTRY {}!!".format(country))
      print(" Uploading datatable of {}".format(country))
      print("    Table shape: {}".format(df.shape))
      print("    Table contents: {}".format(df.columns.to_list()))
      print("    Table ct types: {}".format(df.dtypes.to_list()))
      try:
        # Create the loggin index track
        log_data["country"].append(country)
        log_data["items"].append(df.shape[0])
        pandas_gbq.to_gbq(df, TABLE_ID, project_id=PROJECT_ID, credentials=CREDENTIALS, if_exists='append')
        print("Uploaded!")
      except Exception as e:
        print("Error on uploading {}...".format(e))
    # Save the log file into the log table server
    try:
      log_df = pd.DataFrame({"country": log_data["country"], "days_collected": log_data["items"]})
      pandas_gbq.to_gbq(log_df, TABLE_LOG_ID, project_id=PROJECT_ID, credentials=CREDENTIALS, if_exists="replace")
      print("Log saved into {}!".format(TABLE_LOG_ID))
    except Exception as e:
      print("Not able to save the logging, due to {}".format(e))
    
  print("DONE! -> Process from: {}".format(datetime.now()))

