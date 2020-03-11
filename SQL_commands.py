# External modules: psycopg2 connects to the database. json loads .json files.
import json
import psycopg2

from constants import DESIRED_FIELDS, FIELDS_LENGTH, COLUMNS_TO_SELECT, COLUMNS_TO_INSERT


# Helper function for create_user and modify_hash_code.
def format_hash_code(hash_code):
    hex_hash_code = "\\\\x" + hash_code.hex()
    return hex_hash_code


def create_user(*values_tuple, cur, hash_code, email):
    query = "INSERT INTO users (%s) VALUES (%sE%%s, %%s)" % (COLUMNS_TO_INSERT, '%s, ' * FIELDS_LENGTH)

    parameters_tuple = values_tuple + (format_hash_code(hash_code), email)
    # Uncomment this line for debugging:
    # print('Query: ', query, '\nParameters tuple: ', parameters_tuple)
    cur.execute(query, parameters_tuple)


def modify_user(*values_tuple, cur, email):
    update_list = [("%s = %%s" % item) for item in DESIRED_FIELDS]
    update_string = ', '.join(update_list)
    query = "UPDATE users SET %s WHERE email = %%s" % update_string

    parameters_tuple = values_tuple + (email,)
    # Uncomment this line for debugging:
    # print('Query: ', query, '\nParameters tuple: ', parameters_tuple)
    cur.execute(query, parameters_tuple)


def delete_user(cur, email):
    cur.execute("DELETE FROM users WHERE email = %s", (email,))


def modify_hash_code(cur, hash_code, email):
    hex_hash_code = format_hash_code(hash_code)
    cur.execute("UPDATE users SET hash_code = E%s WHERE email = %s", (hex_hash_code, email))


# Helper function for select_all_users and select_one_user that converts a data record from the cursor into a more
# useful, JSONify-able dictionary.
def get_dict_from_record(record):
    return {k: v for (k, v) in zip(('user_id', 'email') + DESIRED_FIELDS, (*record,))}


def select_all_users(cur):
    cur.execute("SELECT %s FROM users" % COLUMNS_TO_SELECT)
    records = cur.fetchall()
    return [get_dict_from_record(record) for record in records] if records else None


def select_one_user(cur, column, value):
    cur.execute("SELECT %s FROM users WHERE %s = %%s" % (COLUMNS_TO_SELECT, column), (value,))
    record = cur.fetchone()
    return get_dict_from_record(record) if record else None


def query_hash_code(cur, email):
    cur.execute("SELECT hash_code FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    return row[0].tobytes() if row else None


def row_exists(cur, column, value):
    cur.execute("SELECT EXISTS (SELECT * FROM users WHERE %s = %%s)" % column, (value,))
    return cur.fetchone()[0]


def email_exists(cur, email):
    return row_exists(cur, 'email', email)


# With the information from db_config.json, configure the connection to PostgreSQL and the pgAdmin database.
# Returns the cursor object which can be used to run SQL commands.
def config():
    try:
        with open('db_config.json') as file:
            db_data = json.load(file)

        dbname = db_data['dbname']
        dbusername = db_data['dbusername']
        dbpassword = db_data['dbpassword']
        dbhost = db_data['dbhost']
        dbport = db_data['dbport']

        conn = psycopg2.connect(
            "dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (
                dbname, dbusername, dbhost, dbpassword, dbport))
        conn.autocommit = True
        cur = conn.cursor()
        return cur
    except Exception as inst:
        print("There was an error connecting to the database. \nDetails: " + str(inst))
