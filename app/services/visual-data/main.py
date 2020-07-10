from flask                import Flask, request, jsonify, Response
from flask_restful        import Resource, Api
from flask_request_params import bind_request_params

import sys
import json
import pandas as pd

from google.cloud import bigquery
from google.oauth2 import service_account


# GCloud authentication process
JSON_KEY_PATH = './keys/epidemicapp-62d0d471b86f.json'
CREDENTIALS = service_account.Credentials.from_service_account_file(JSON_KEY_PATH)
PROJECT_ID = "epidemicapp-280600"
USERS_PREDICTION_DATASET_ID = "users_prediction."
USERS_DATASET_ID = "users_data."
USERS_LOG_TABLE_ID = "users_log.process_log_content"

LOG_QUERY = """SELECT * FROM {};"""

# Initialize the restful app
app = Flask(__name__)
api = Api(app)
app.before_request(bind_request_params)


class visual_predictions(Resource):
  
  def get(self):

    try:
      main_id = request.args.get("id")
      user_table_id = "users_data.{}".format(main_id)

      table_id = "users_prediction.{}".format(main_id)

      bigquery_client = bigquery.Client(project=PROJECT_ID, credentials=CREDENTIALS)
      df = bigquery_client.query(LOG_QUERY.format(table_id)).to_dataframe()
      df["date"] = df["date"].apply(lambda d: d.isoformat().split("T")[0])

      response = df.to_dict()
    except Exception as e:
      response = {
        "erro": "Internal server error...", 
        "details": "{}".format(e)
      }
    return response


class visual_real_data(Resource):

  def get(self):

    try:
      main_id = request.args.get("id")
      user_table_id = "users_data.{}".format(main_id)

      bigquery_client = bigquery.Client(project=PROJECT_ID, credentials=CREDENTIALS)
      df = bigquery_client.query(LOG_QUERY.format(user_table_id)).to_dataframe()

      response = df.to_dict()
    except Exception as e:
      response = {
        "erro": "Internal server error...", 
        "details": "{}".format(e)
      }
    return response


# Append each URL resource
api.add_resource(visual_predictions, '/predictions')
api.add_resource(visual_real_data, '/real_data')

if __name__ == '__main__':
  app.run(port = 5000, debug = True)