from psycopg2 import connect
from flask import request
from os import path

from config.APIConfig import db_data

dirname = path.dirname(__file__)
APIConfig_filename = path.join(dirname, '../config/APIConfig.json')

db_name = db_data['dbname']
db_username = db_data['dbusername']
db_password = db_data['dbpassword']
db_host = db_data['dbhost']
db_port = db_data['dbport']

conn_info = (db_name, db_username, db_password, db_host, db_port)


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


def get_conn(dbname, dbusername, dbpassword, dbhost, dbport):
    conn = connect(
        "dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (
            dbname, dbusername, dbpassword, dbhost, dbport))
    conn.autocommit = True
    return conn


def check_regular_user_verified_username(user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username FROM check_regular_user_verified_username(%s);", (user_id,))
            return cur.fetchone()[0]

def format_binary(binary_data):
    return "\\\\x" + binary_data.hex()
