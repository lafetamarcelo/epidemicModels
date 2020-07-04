from flask                import Flask, request, jsonify, Response
from flask_restful        import Resource, Api
from flask_request_params import bind_request_params

import re
import io
import sys
import json
import datetime
import random
import pandas as pd


def validate_email(email):
  regex = '^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w+(\.\w+)*$'
  if re.search(regex, email.lower()): 
    return True
  return False


# Initialize the restful app
app = Flask(__name__)
api = Api(app)
app.before_request(bind_request_params)

DEF_COLUMNS = [""]

# Define the services jobs
class validate_content(Resource):

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
      response.response = json.dumps({"erro": "No email/output", "detail": "{}".format(e)})
      return response
      
    # Getting file content
    try:
      f = request.files['file']
      if not f:
        response.response = json.dumps({"erro": "No file"})
        return response
    except Exception as e:
      response.response = json.dumps({"erro": "No file", "detail": "{}".format(e)})
      return response
    
    try:
      # Data checks
      stream = io.StringIO(f.stream.read().decode("UTF8"))
      df = pd.read_csv(stream, sep=",")
      # (1) check -> If enough data
      if len(df) < 8:
        response.response = json.dumps({"erro": "Not enought lines on file"})
        return response
      # (2) check -> If columns has size
      if len(df.columns) != 7:
        response.response = json.dumps({"erro": "Columns size does not match"})
        return response
      # (3) check -> If columns names does not match
      if len(df.columns) != 7:
        response.response = json.dumps({"erro": "Columns size does not match"})
        return response
      
      # Email checks
      # (1) check -> If @ in email
      if not validate_email(email):
        response.response = json.dumps({"erro": "Invalid email"})
        return response

      # (2) check -> If Tiago Bolinha
      if ("tiago.eem" in email) or ("tiago.sanches" in email):
        response.response = json.dumps({"erro": "Tiago"})
        return response

      # Output checks
      # (1) check -> If output type match options
      if output_type not in ["jupyter", "pdf", "report"]:
        response.response = json.dumps({"erro": "Output type does not exist"})
        return response

      response.response = json.dumps({"OK": True})
      response.status_code = 200

      # Upload data...



      return response
    except Exception as e:
      print("  -> validate-file error: {}".format(e))
      response.response= json.dumps({"erro": "Internal server error", "detail": "{}".format(e)})
      response.status_code = 500
      return response

# class upload_content(Resource):

#   def post(self):

#     self.



# Create each resource...
api.add_resource(validate_content, '/validate_file')
# api.add_resource(upload_content, '/upload_file')

if __name__ == '__main__':
  app.run(port = 5000, debug = True)