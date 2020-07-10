from flask                import Flask, request, jsonify, Response
from flask_restful        import Resource, Api
from flask_request_params import bind_request_params
from flask_cors           import CORS

import re
import io
import sys
import json
import datetime
import pandas as pd

from google.cloud import bigquery, tasks_v2
from google.oauth2 import service_account

# GCloud authentication process
JSON_KEY_PATH = './keys/epidemicapp-62d0d471b86f.json'
CREDENTIALS = service_account.Credentials.from_service_account_file(JSON_KEY_PATH)


# Support functions

def validate_email(email):
  regex = '^\w+[._]?\w+([._]?\w*)*[@]\w+[.]\w+([.]\w+)*$'
  if re.search(regex, email.lower()): 
    return True
  return False

#
# Support Global variables
#
#  
DEF_COLUMNS = ["index","date","deaths","confirmed","active",
  "recovered","new_confirmed","new_recovered","new_deaths","habitantes"]
#
#
USERS_DATASET_ID = "users_data."
USERS_LOG_TABLE_ID = "users_log.process_log_content"
#
# 
PROJECT_ID = "epidemicapp-280600"
QUEUE_LOCATION = "southamerica-east1"
QUEUE_ID = "user-process-queue"
QUEUE_SERVICE_URL = "https://user-process-dot-epidemicapp-280600.rj.r.appspot.com/process_file"


# Initialize the restful app
app = Flask(__name__)
CORS(app)
api = Api(app)
app.before_request(bind_request_params)


#
# Define the services jobs
#

class validate_content(Resource):
  """

  """

  def post(self):
    
    response = Response(mimetype='application/json')
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.status_code = 400
    
    try:
      # Getting email
      email = request.form["email"]
      # Getting output type
      output_type = request.form["output"]
    except Exception as e:
      response.response = json.dumps({"erro": "Email inválido.", "detail": "{}".format(e)})
      return response
      
    # Getting file content
    try:
      f = request.files['file']
      if not f:
        response.response = json.dumps({"erro": "Sem arquivo."})
        return response
    except Exception as e:
      response.response = json.dumps({"erro": "Sem arquivo.", "detail": "{}".format(e)})
      return response
    
    try:
      # Data checks
      stream = io.StringIO(f.stream.read().decode("UTF8"))
      df = pd.read_csv(stream, sep=",")
      # (1) check -> If enough data
      if len(df) < 8:
        response.response = json.dumps({"erro": "Arquivo com poucas amostras."})
        return response
      # (2) check -> If columns has size
      if len(df.columns) != len(DEF_COLUMNS):
        response.response = json.dumps({
          "erro": "Tamanho das colunas inválido.", 
          "details": "File has {} columns...".format(len(df.columns))})
        return response
      # (3) check -> If columns names does not match
      if len(df.columns) != len(DEF_COLUMNS):
        response.response = json.dumps({
          "erro": "Tamanho das colunas inválido.",
          "details": "File has {} columns...".format(len(df.columns))})
        return response
      
      # Email checks
      # (1) check -> If @ in email
      if not validate_email(email):
        response.response = json.dumps({"erro": "Email inválido."})
        return response

      # (2) check -> If Tiago Bolinha
      if ("tiago.eem" in email) or ("tiago.sanches" in email):
        response.response = json.dumps({"erro": "Tiago"})
        return response

      # Output checks
      # (1) check -> If output type match options
      if output_type not in ["jupyter", "pdf", "report"]:
        response.response = json.dumps({"erro": "Informe o tipo de saída."})
        return response

      response.response = json.dumps({"OK": True})
      response.status_code = 200

    except Exception as e:
      print("  -> validate-file error: {}".format(e))
      response.response = json.dumps({"erro": "Erro interno do servidor", "detail": "{}".format(e)})
      response.status_code = 500

    # Upload data...
    if response.status_code == 200:
      # Upload table content to Big Query
      response.status_code, response.response = upload_data_content(data=df, email=email, output_type=output_type)

    return response


#
# Processing functions
#


def upload_data_content(data=None, email=None, output_type=None):
  """
  """

  if (email == None) or (output_type == None) or (data is None):
    return 500, json.dumps({"erro": "Algum erro aconteceu no processamento inicial dos dados..."})
  #
  #
  #
  try:
    # Create the Google Cloud - Big Query Client
    client = bigquery.Client(project=PROJECT_ID, credentials=CREDENTIALS)
    # Create the table id
    current_time = datetime.datetime.now()
    table_id = USERS_DATASET_ID + "{}_{}".format(
      email.split("@")[0], 
      current_time
    ).replace(" ", "").replace(":", "").replace(".", "").replace("-", "")
    # Changing the columns name
    data = data[DEF_COLUMNS[1:]]
  except Exception as e:
    return 500, json.dumps({
      "erro": "Erro interno do servidor. Tente mais tarde!",
      "details": "Error at Big Query Client creating => {}".format(e)})
  #
  #
  #
  try:
    job = client.load_table_from_dataframe(data, table_id, job_config=bigquery.LoadJobConfig())
    job.result() # Wait for the job to complete.
  except Exception as e:
    return 500, json.dumps({
      "erro": "Erro interno do servidor. Tente mais tarde!",
      "details": "Error at Big Query loading job => {}".format(e)})
  #
  #
  #
  try:
    job = update_user_log(email, table_id, output_type)
    job.result() # Wait for the job to complete.
  except Exception as e:
    return 500, json.dumps({
      "erro": "Erro interno do servidor. Tente mais tarde!",
      "details": "Error at Big Query users log loading job => {}".format(e)})
  #
  #
  #
  try:
    response_ = queue_task(email, table_id, output_type)
  except Exception as e:
    return 500, json.dumps({
      "erro": "Erro interno do servidor. Tente mais tarde!",
      "details": "Error at queue task including => {}".format(e)})
  ###
  #   -> 
  ###
  return 200, json.dumps({"OK": True, "scheduler_response":"{}".format(response_)})


def update_user_log(email=None, table_id=None, output_type=None):
  """
  """
  # Create the Big Query Client
  client = bigquery.Client(project=PROJECT_ID, credentials=CREDENTIALS)
  # Query to include user at the logging
  sql = """
    INSERT INTO users_log.process_log_content
    VALUES ('{}', '{}', '{}', {}, '{}');
  """.format(email, table_id, datetime.datetime.now(), False, output_type)
  # Execute the query job and include the new user
  return client.query(sql, job_config=bigquery.QueryJobConfig())


def queue_task(email=None, table_id=None, output_type=None):
  """
  """

  # Create the Task Client
  client = tasks_v2.CloudTasksClient(credentials=CREDENTIALS)

  # Specify the cloud task in hand
  parent = client.queue_path(PROJECT_ID, QUEUE_LOCATION, QUEUE_ID)

  # Build the task structure
  task = {
    'http_request': {  # Specify the type of request.
      'http_method': 'POST',
      'url': QUEUE_SERVICE_URL  # The full url path that the task will be sent to.
    }
  } 

  # Create the task payload
  payload = json.dumps({"email":email, "table_id":table_id, "output_type":output_type})
  converted_payload = payload.encode()
  # Add the payload to the taks
  #task['app_engine_http_request']['body'] = converted_payload
  task['http_request']['body'] = converted_payload
  # Create the task and request
  # Use the client to build and send the task.
  response = client.create_task(parent, task)

  return response
  
  

# Create each resource...
api.add_resource(validate_content, '/upload_file')

if __name__ == '__main__':
  app.run(port = 5000, debug = True)