from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

from routes import register_routes

register_routes(app)