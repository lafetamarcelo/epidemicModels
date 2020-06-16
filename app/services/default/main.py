from flask                import Flask, request, jsonify
from flask_restful        import Resource, Api
from flask_request_params import bind_request_params

# Initialize the restful app
app = Flask("default_route_app")
api = Api(app)
app.before_request(bind_request_params)

if __name__ == '__main__':
  app.run(port = 5000, debug = True)