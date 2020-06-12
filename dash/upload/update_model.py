
import os
import pickle
import requests
import pandas_gbq


import pandas as pd
import numpy as np

from PyAstronomy import pyasl
from datetime import datetime, timedelta
from google.oauth2 import service_account

from models import *

project_id = "epidemicmodels"
pred_table_id = "models_data.predictions"
par_table_id = "models_data.parameters"
credentials = service_account.Credentials.from_service_account_file('../gkeys/epidemicModels-1fc10954f61b.json')


# Configuration variables
COUNTRY = "CN"
LOG_FILE = "./log_models.pickle"
START_SIZE = 1000
PEAK_EXISTS = True



if __name__ == "__main__":

  print("Running update on : {} ...".format(COUNTRY))

  # Get the model data
  covid_api = 'https://corona-api.com/countries/'
  rest_countries = 'https://restcountries.eu/rest/v2/alpha/'
  data_json =  requests.get(covid_api + COUNTRY).json()
  country = requests.get(covid_api + COUNTRY).json()
  N = data_json['data']['population']

  print("Organizing the data...")
  
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
  if COUNTRY == "BR":
    df.iloc[135,:] = [df.iloc[135, 0]] + [None]*7
    df = df.interpolate(method ='linear', limit_direction ='forward')
    df = df.where(df.active != 0.0).dropna()
  # Creating the time vector --- for plotly
  datetime_64 = df["date"].values
  ts = (datetime_64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
  time = [datetime.utcfromtimestamp(t) for t in ts]

  print("Reading the model log...")

  if os.path.isfile(LOG_FILE):
    with open(LOG_FILE, "rb") as handle:
      log_data = pickle.load(handle)
  else:
    log_data = dict()

  print("Creating SIR data...")

  start_moment = np.argmax(df["active"].to_numpy() >= START_SIZE)
  time_ref = time[start_moment:]
  I = df['active'].to_numpy()[start_moment:]
  R = df['recovered'].to_numpy()[start_moment:]
  M = df['deaths'].to_numpy()[start_moment:]
  S = N - R - I
  # Creating the time vector
  t = np.linspace(0, len(I)-1, len(I))

  Sd, Id, Md, Rd, td = S, I, M, R, t

  print("Running the time shift learning...")

  saved_param = {'Ro':[], 'D':[], 'pop':[], "date":[]}
  saved_prediction = {"S":[], "I":[], "R":[], "date":[], "at_date":[]}

  start_day = 8 # Starting with 8 day points
  if COUNTRY in log_data.keys():
    start_day = log_data[COUNTRY]["start_day"]
  else:
    log_data[COUNTRY] = dict()

  if start_day < len(I)-1:
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
      at_date = [current_date]*len(pred_t)
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
      saved_prediction["at_date"] += at_date
      # Print the progress...
      print("߷ Run {} of {}".format(i-start_day+1, len(I)-start_day))
    
    print("Determining the peak...")
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

    # Transform all in lists
    for item in ["S", "I", "R"]:
      auxiliar_list = []
      for data in saved_prediction[item]:
        auxiliar_list += data.tolist()
      saved_prediction[item] = auxiliar_list

    print("Processing done... Upload to cloud: (y/n)")
    input_data = input()
    if input_data.upper() == "Y":
      # Build the data tables to upload
      print("Uploading the parameters...")
      par_df = pd.DataFrame(data=saved_param)
      par_df["country"] = COUNTRY # Create the country column
      par_df["peak_est"] = peak_date # Creating the column of peak dates
      pandas_gbq.to_gbq(par_df, par_table_id, project_id=project_id, credentials=credentials, if_exists='append')
      
      print("Uploading the predictions...")
      pred_df = pd.DataFrame(data=saved_prediction)
      pred_df["country"] = COUNTRY # Create the country column
      pandas_gbq.to_gbq(pred_df, pred_table_id, project_id=project_id, credentials=credentials, if_exists='append')

      # Update the logging values
      print("Updating the log...")
      log_data[COUNTRY]["start_day"] = len(I)

      print("Saving log data...")
      # Saving the log file
      with open(LOG_FILE, "wb") as handle:
        pickle.dump(log_data, handle)

  else:
    print("߷ Nothing to update...")

  print("DONE!")


  




