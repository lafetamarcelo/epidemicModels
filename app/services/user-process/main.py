from flask                import Flask, request, jsonify, Response
from flask_restful        import Resource, Api
from flask_request_params import bind_request_params

import re
import io
import sys
import json
import datetime
import numpy as np
import pandas as pd

from models import *

from datetime import datetime, timedelta
from google.cloud import bigquery, tasks_v2
from google.oauth2 import service_account


# GCloud authentication process
JSON_KEY_PATH = './keys/epidemicapp-62d0d471b86f.json'
CREDENTIALS = service_account.Credentials.from_service_account_file(JSON_KEY_PATH)
PROJECT_ID = "epidemicapp-280600"
USERS_PREDICTION_DATASET_ID = "users_prediction."
USERS_DATASET_ID = "users_data."
USERS_LOG_TABLE_ID = "users_log.process_log_content"

# Initialize the restful app
app = Flask(__name__)
api = Api(app)
app.before_request(bind_request_params)


class process_user_file(Resource):
  """
  """
  
  def post(self):
    """
    """

    response = Response(mimetype='application/json')
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.status_code = 400

    ## Accessing user data
    # Getting the user payload info, and accessing the 
    # stored information on the database.
    try:
      payload_text = request.get_data(as_text=True) or '(empty payload)'
      print(payload_text)

      payload_data = json.loads(payload_text) # Load data to dictionary
      print(payload_data)

      user_email = payload_data["email"] # Get the user email
      user_table_id = payload_data["table_id"] # Get the user table id
      user_output_type = payload_data["output_type"] # Get the analysis output type

      # Get the user content
      bigquery_client = bigquery.Client(project=PROJECT_ID, credentials=CREDENTIALS)
      sql = """
        SELECT * 
        FROM {}
      """.format(user_table_id)
      df = bigquery_client.query(sql).to_dataframe()
    except Exception as e:
      response.status_code = 500
      print("Exception at Accessing user data: {}".format(e))
      response.response = json.dumps({
        "erro": "Erro interno do servidor. Por favor tente mais tarde!",
        "details": "Error accessing user data...",
        "exception": "Exception -> {}".format(e)})
      return response
    
    ## Processing the data for machine learning
    # 
    #
    try:
      ## Create the constant values
      # Process the date to datetime
      initial_date = datetime.fromisoformat(df["date"].iloc[0])
      # Get the population size
      pop = df["habitantes"].iloc[0]
      ## Compute each component of model
      # Compute the value of the active cases

      # Getting the model components
      I = np.array(df["active"].tolist())
      R = np.array(df["recovered"].tolist())
      D = np.array(df["deaths"].tolist())
      S = pop - I - R - D
      ## Trainning the model
      # Creating the train dataset
      dataset = dict(S=S, I=I, R=R, D=D)
      td = np.linspace(0, len(I)-1, len(I))
      # Creating the prediction model
      model = ss.SIR(pop=pop, focus=["S","I","R","D"], verbose=False)
      # Trainning the state model
      model.fit(dataset, td,  
        search_pop=True,
        pop_sens=[0.00001, 0.05],
        Ro_sens=[0.8, 15], 
        D_sens=[5, 60],
        mu_sens=[0.0001, 0.02])
      ## Predicting the components
      # Creating the values for prediction
      sim_time = np.linspace(0, len(I)+120-1, len(I)+120)
      sim_date = [initial_date + timedelta(days=i) for i in sim_time]
      sim_initial = (S[0], I[0], R[0], D[0])
      sim_res = model.predict(sim_initial, sim_time)
      ## Create the answer dataframe
      # Building the dataframe      
      res_df = pd.DataFrame({
        "date": sim_date,
        "suceptible": sim_res[0],
        "active": sim_res[1],
        "recovered": sim_res[2],
        "deaths": sim_res[3]
      })
    except Exception as e:
      response.status_code = 500
      print("Exception at Processing the data: {}".format(e))
      response.response = json.dumps({
        "erro": "Erro interno do servidor. Por favor tente mais tarde!",
        "details": "Error accessing user data...",
        "exception": "Exception -> {}".format(e)})
      return response
    
    ## Upload user predictions
    #
    # 
    try:
      # Create the prediction table id
      pred_table_id = USERS_PREDICTION_DATASET_ID + user_table_id.split(".")[1]
      # Upload the predictions to the new prediction table id
      job = bigquery_client.load_table_from_dataframe(res_df, pred_table_id, job_config=bigquery.LoadJobConfig())
      job.result() # Wait for the job to complete.
    except Exception as e:
      response.status_code = 500
      print("Exception at Uploading user predictions: {}".format(e))
      response.response = json.dumps({
        "erro": "Erro interno do servidor. Por favor tente mais tarde!",
        "details": "Error uploading user predictions...",
        "exception": "Exception -> {}".format(e)})
      return response
    
    ## Upload user parameters
    #
    # 
    try:
      # Create the prediction table id
      pred_table_id = USERS_PREDICTION_DATASET_ID + user_table_id.split(".")[1]
      # Upload the predictions to the new prediction table id
      # Query to include user at the logging
      sql = """
        INSERT INTO users_log.estimation_log_parameters
        VALUES ('{}', '{}', {}, {}, {}, {});
      """.format(user_email, user_table_id, model.parameters[0], model.parameters[1], model.parameters[2], model.parameters[3])
      # Execute the query job and include the new user
      job = bigquery_client.query(sql, job_config=bigquery.QueryJobConfig())
      job.result()
    except Exception as e:
      response.status_code = 500
      print("Exception at Uploading user parameters {}".format(e))
      response.response = json.dumps({
        "erro": "Erro interno do servidor. Por favor tente mais tarde!",
        "details": "Error uploading user parameters...",
        "exception": "Exception -> {}".format(e)})
      return response

    ## Update the user logging table
    #
    #
    try:
      # Create the prediction table id
      pred_table_id = USERS_PREDICTION_DATASET_ID + user_table_id.split(".")[1]
      # Upload the predictions to the new prediction table id
      # Query to include user at the logging
      sql = """
        UPDATE users_log.process_log_content
        SET processed = True
        WHERE table_id='{}';
      """.format(user_table_id)
      # Execute the query job and include the new user
      job = bigquery_client.query(sql, job_config=bigquery.QueryJobConfig())
      job.result()
    except Exception as e:
      response.status_code = 500
      print("Exception at Updating user log table {}".format(e))
      response.response = json.dumps({
        "erro": "Erro interno do servidor. Por favor tente mais tarde!",
        "details": "Error updating the user log table...",
        "exception": "Exception -> {}".format(e)})
      return response

    ## Build email task for user
    #
    #

    response.response = json.dumps({"OK": True, "details": "Task successful."})
    response.status_code = 200

    return response

# Append each URL resource
api.add_resource(process_user_file, '/process_file')

if __name__ == '__main__':
  app.run(port = 5000, debug = True)