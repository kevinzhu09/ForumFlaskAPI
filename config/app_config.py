# External modules: flask handles the URI routes for the API requests. It also allows JSON to be easily written.
# flask_jwt_extended handles the JSON Web Tokens (JWT) integration which is used for login verification.
# flask_mail handles the mail server.
# json helps for reading .json files.
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from json import load
from os import path
from flask_cors import CORS
from constants import APP_URI

# Configuration for the Flask app, JWT integration and mail server:
basedir = path.abspath(path.dirname(__file__))
app = Flask(__name__, template_folder=path.join(basedir, '../templates'))

cors = CORS(app, resources={r"/*": {"origins": APP_URI}})


with open(path.join(basedir, 'mail_JWT_config.json')) as file:
    mail_JWT_data = load(file)

app.config['JWT_SECRET_KEY'] = mail_JWT_data['JWT_SECRET_KEY']
app.config['MAIL_SERVER'] = mail_JWT_data['MAIL_SERVER']
app.config['MAIL_PORT'] = mail_JWT_data['MAIL_PORT']
app.config['MAIL_USERNAME'] = mail_JWT_data['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = mail_JWT_data['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = mail_JWT_data['MAIL_USE_TLS']
app.config['MAIL_USE_SSL'] = mail_JWT_data['MAIL_USE_SSL']

jwt = JWTManager(app)
mail = Mail(app)

# With the information from db_config.json, configure the connection to the PostgreSQL database.
# Saves the connection information in a tuple.


with open(path.join(basedir, 'db_config.json')) as file:
    db_data = load(file)

dbname = db_data['dbname']
dbusername = db_data['dbusername']
dbpassword = db_data['dbpassword']
dbhost = db_data['dbhost']
dbport = db_data['dbport']

conn_info = (dbname, dbusername, dbpassword, dbhost, dbport)


# Helper function for the API. It allows the API to accept requests in either JSON or through form-data.
def request_dynamic(request_is_json, allow_null=False):
    if allow_null:
        if request_is_json:
            return lambda value: request.json.get(value)
        else:
            return lambda value: request.form.get(value)
    else:
        if request_is_json:
            return lambda value: request.json[value]
        else:
            return lambda value: request.form[value]
