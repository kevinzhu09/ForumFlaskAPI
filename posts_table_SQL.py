# External modules: psycopg2 connects to the database. json loads .json files.
import psycopg2


def get_conn(dbname, dbusername, dbpassword, dbhost, dbport):
    conn = psycopg2.connect(
        "dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (
            dbname, dbusername, dbpassword, dbhost, dbport))
    conn.autocommit = True
    return conn
