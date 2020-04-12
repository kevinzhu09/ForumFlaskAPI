# External modules: psycopg2 connects to the database. json loads .json files.
import psycopg2
from flask import request
from os import path

# from .. import APIConfig
from config.APIConfig import db_data

# With the information from db_config.json, configure the connection to the PostgreSQL database.
# Saves the connection information in a tuple.

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
    conn = psycopg2.connect(
        "dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (
            dbname, dbusername, dbpassword, dbhost, dbport))
    conn.autocommit = True
    return conn


def check_verified(conn, user_id):
    with get_conn(*conn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username FROM users WHERE user_id = %s AND verified = TRUE", (user_id,))
            return cur.fetchone()[0]


# Helper function for insert_user and update_hash_code.
def format_binary(binary_data):
    return "\\\\x" + binary_data.hex()