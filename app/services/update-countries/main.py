from flask                import Flask, request, jsonify
from flask_restful        import Resource, Api
from flask_request_params import bind_request_params

import json
import datetime
import random

from job import *


# Initialize the restful app
app = Flask(__name__)
api = Api(app)
app.before_request(bind_request_params)

# Create each resource...
api.add_resource(upd_data.real_data_trigger, '/updatedata')
api.add_resource(upd_model.train_all_trigger, '/trainall')

if __name__ == '__main__':
  app.run(port = 5000, debug = True)