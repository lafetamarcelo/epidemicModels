from flask                import Flask, request, jsonify
from flask_restful        import Resource, Api
from flask_request_params import bind_request_params

import os
import pickle
import requests
import pandas_gbq

import pandas as pd
import numpy  as np

from PyAstronomy   import pyasl
from datetime      import datetime, timedelta
from google.oauth2 import service_account

from models import *

# Defualt variables
PROJECT_ID    = "epidemicmodels"
PRED_TABLE_ID = "countries.predictions"
PAR_TABLE_ID  = "countries.parameters"

TABLE_LOG_ID  = "countries.model_log"
LOG_QUERY     = "SELECT * FROM countries.model_log"

CREDENTIALS   = service_account.Credentials.from_service_account_file('./keys/epidemicModels-1fc10954f61b.json')
pandas_gbq.context.credentials = CREDENTIALS

# Configuration variables
COUNTRY_LIST = ["DE", "CN", "IT", "BR"]

SETUP_COUNTRY = {
  "BR": {
    "start_size": 4000,
    "peak_exist": False
  },
  "CN": {
    "start_size": 2000,
    "peak_exist": True
  },
  "DE": {
    "start_size": 2000,
    "peak_exist": True
  },
  "IT": {
    "start_size": 2000,
    "peak_exist": True
  }
}


class train_all_trigger(Resource):
  def get(self):
    # Call the update all countries 
    # pipeline 
    # 
    train_all_countries_pipe()


def train_all_countries_pipe():
  """
  """
  for country in COUNTRY_LIST:
    train_country_pipe(country=country)


def train_country_pipe(country=None):
  """
  """
  
  # Setting some control variables
  START_SIZE = SETUP_COUNTRY[country]["start_size"]
  PEAK_EXISTS = SETUP_COUNTRY[country]["peak_exist"]

  print("Running update on : {} ...".format(country))

  # Get the model data
  covid_api = 'https://corona-api.com/countries/'
  rest_countries = 'https://restcountries.eu/rest/v2/alpha/'
  data_json =  requests.get(covid_api + country).json()
  # country = requests.get(covid_api + country).json()
  N = data_json['data']['population']

  print("\t(1) Organizing the data...")
  
  # Creating the dataframe with the data
  df = pd.DataFrame(data_json['data']['timeline'])
  df = df.sort_values('date').reset_index()
  df['date'] = [datetime.fromisoformat(f) for f in df['date']]
  df = df.drop_duplicates(subset='date', keep = 'last')
  # Criando o vetor de tempo
  first_date = df['date'].iloc[0]
  size_days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
  date_vec = [first_date + timedelta(days=k) for k in range(size_days)]
  new_df = pd.DataFrame(date_vec, columns=['date'])
  new_df = pd.merge(new_df, df, how='left', on='date')
  new_df = new_df.drop(columns= ['index',  'updated_at', 'is_in_progress'])
  for col in new_df.columns[1:]:
    new_df[col] = new_df[col].interpolate(method='polynomial', order=1)
  df = new_df.dropna()
  
  # Solve particular problems
  # 
  # For Brazil, the measure on day 135 has an incorrect value
  # so we interpolate that measure to not loose the final of 
  # the time series.
  if country == "BR":
    df.iloc[135,:] = [df.iloc[135, 0]] + [None]*7
    df = df.interpolate(method ='linear', limit_direction ='forward')
    df = df.where(df.active != 0.0).dropna()
  
  # Creating the time vector --- for plotly
  datetime_64 = df["date"].values
  ts = (datetime_64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
  time = [datetime.utcfromtimestamp(t) for t in ts]

  print("\t(2) Reading the model log...")
  # If the model log does not exist, we create a model log 
  # with a particular structure -> dictionary
  
  try:
    # Reading the log table...
    log_df = pandas_gbq.read_gbq(LOG_QUERY, project_id=PROJECT_ID)
    country_list = log_df["country"].to_list()
    start_p_list = log_df["start_point"].to_list()
    log_data = dict(zip(country_list, start_p_list))
  except:
    log_data = dict()
    print("\t\tCountry log table does not yet, exist...")
    

  print("\t(3) Creating SIR data...")
  # Create the SIR model structure, for the model trainning
  start_moment = np.argmax(df["active"].to_numpy() >= START_SIZE)
  time_ref = time[start_moment:]
  I = df['active'].to_numpy()[start_moment:]
  R = df['recovered'].to_numpy()[start_moment:]
  M = df['deaths'].to_numpy()[start_moment:]
  S = N - R - I
  # Creating the time vector
  t = np.linspace(0, len(I)-1, len(I))
  # Create the trainning variables
  Sd, Id, Md, Rd, td = S, I, M, R, t

  print("\t(4) Running the time shift learning...")
  # Create the structures to save the time shift results
  saved_param = {'Ro':[], 'D':[], 'pop':[], "date":[]}
  saved_prediction = {"S":[], "I":[], "R":[], "date":[], "at_date":[]}

  # Check if the country exists in the logging
  # if does not, create the logging structure
  # for the country, if exists, start the 
  # time shift learning from the logged one
  start_day = 8 # Starting with 8 day points
  if country in log_data.keys():
    start_day = log_data[country]

  # If start_day on the logging is less than 
  # the size of the data, there is room for 
  # running windowed shifting learning
  if start_day < len(I):
    # If peak does not exists, predict 
    # 120 days ahead to find the peak
    if PEAK_EXISTS:
      pred_t = range(int(td[-1]))
    else:
      pred_t = range(int(td[-1])+120)
    # Compute the time vector
    time_vector = [time_ref[0] + timedelta(days=i) for i in pred_t]
    pred_t = np.array(pred_t)
    for i in range(start_day, len(I)):    
      # Compute this day data...
      current_date = time_ref[0] + timedelta(days=i)
      current_date_vector = [current_date]*len(pred_t)
      # Get a partial window of the dataset
      dataset = dict(S=Sd[:i], I=Id[:i], R=Rd[:i])
      # Create the model
      sir_model = ss.SIR(pop=N, focus=["S", "I", "R"], verbose=False)
      # Adjust the parameters
      sir_model.fit(dataset, td[:i],
                    search_pop=True,
                    pop_sens=[0.001, 0.05],
                    Ro_sens=[0.8, 15.0], 
                    D_sens=[5.0, 40.0])
      # Save the estimated parameters
      saved_param['Ro'].append(sir_model.parameters[0])
      saved_param['D'].append(sir_model.parameters[1])
      saved_param['pop'].append(sir_model.parameters[2])
      saved_param['date'].append(current_date)
      # Save the model prediction
      result = sir_model.predict((Sd[0], Id[0], Rd[0]), pred_t)
      saved_prediction["S"].append(result[0])
      saved_prediction["I"].append(result[1])
      saved_prediction["R"].append(result[2])
      saved_prediction["date"] += time_vector
      saved_prediction["at_date"] += current_date_vector
      # Print the progress...
      print("\t\t߷ Run {} of {}".format(i-start_day+1, len(I)-start_day))
    
    print("\t(5) Determining the peak...")
    if PEAK_EXISTS:
      # Compute the derivative of the smoothed 
      # active infected time series
      dI = np.gradient(pyasl.smooth(I, 13, "hamming"))
      t = np.linspace(0, len(dI), len(dI))
      # Find the derivative bigger then zero
      signal = np.array([di >= 0 for di in dI[::-1]])
      # Find the first point where the derivative
      # change signal
      peak_pos = int(len(Id) - np.argmax(signal))
      peak_date = [time[0] + timedelta(days=peak_pos)] * len(saved_param["D"])
    else:
      estimated_peaks = []
      for data in saved_prediction["I"]:
        # Computing the prediction derivative
        dI = np.gradient(data)
        # Computing the derivative signal
        signal_pred = np.array([di >= 0 for di in dI[::-1]])
        # Computing the peak estimate point
        # print("Signal shape: ", len(data) - np.argmax(signal_pred))
        estimated_peaks.append(len(data) - np.argmax(signal_pred))
      # print(estimated_peaks)
      peak_date = [time_ref[0] + timedelta(days=int(p)) for p in estimated_peaks]

    print("\t(6) Transforming data to lists...")
    # Transform all in lists
    for item in ["S", "I", "R"]:
      auxiliar_list = []
      for data in saved_prediction[item]:
        auxiliar_list += data.tolist()
      saved_prediction[item] = auxiliar_list

    print("\t(7) Uploading data to cloud...")
    try:
      # Build the data tables to upload
      print("\t\tUploading the parameters...")
      par_df = pd.DataFrame(data=saved_param)
      par_df["country"] = country # Create the country column
      par_df["peak_est"] = peak_date # Creating the column of peak dates
      pandas_gbq.to_gbq(par_df, PAR_TABLE_ID, project_id=PROJECT_ID, credentials=CREDENTIALS, if_exists='append')
      
      print("\t\tUploading the predictions...")
      pred_df = pd.DataFrame(data=saved_prediction)
      pred_df["country"] = country # Create the country column
      pandas_gbq.to_gbq(pred_df, PRED_TABLE_ID, project_id=PROJECT_ID, credentials=CREDENTIALS, if_exists='append')

      # Update the logging values
      print("\t\tUpdating the log...")
      log_data[country] = len(I)
    except:
      print("\t\tCloud uploading error!")
    
    # Saving the log data into the cloud
    print("\t(8) Saving log data...")
    try:
      log_upload = {"country":[], "start_point":[]}
      for c in log_data.keys():
        log_upload["country"].append(c)
        log_upload["start_point"].append(log_data[c])
      df_log = pd.DataFrame(log_upload)
      pandas_gbq.to_gbq(df_log, TABLE_LOG_ID, project_id=PROJECT_ID, credentials=CREDENTIALS, if_exists="replace")
    except Exception as e:
      print("\t\tUnable to upload log due to {}".format(e))
  else:
    print("\t߷ Nothing to update...")

  print("DONE! -> Model Update - Process from: {}".format(datetime.now()))

