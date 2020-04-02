from flask import request
from json import load
from os import path

# With the information from db_config.json, configure the connection to the PostgreSQL database.
# Saves the connection information in a tuple.

dirname = path.dirname(__file__)
db_filename = path.join(dirname, 'db_config.json')

with open(db_filename) as file:
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
