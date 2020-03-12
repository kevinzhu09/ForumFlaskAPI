# External modules: psycopg2 connects to the database. json loads .json files.
import psycopg2

from constants import DESIRED_FIELDS, FIELDS_LENGTH, COLUMNS_TO_SELECT, COLUMNS_TO_INSERT


# Helper function for insert_user and update_hash_code.
def format_hash_code(hash_code):
    hex_hash_code = "\\\\x" + hash_code.hex()
    return hex_hash_code


def insert_user(*values_tuple, conn_info, hash_code, email):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            query = "INSERT INTO users (%s) VALUES (%sE%%s, %%s)" % (COLUMNS_TO_INSERT, '%s, ' * FIELDS_LENGTH)

            parameters_tuple = values_tuple + (format_hash_code(hash_code), email)
            # Uncomment this line for debugging:
            # print('Query: ', query, '\nParameters tuple: ', parameters_tuple)
            cur.execute(query, parameters_tuple)


def update_user(*values_tuple, conn_info, email):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            update_list = [("%s = %%s" % item) for item in DESIRED_FIELDS]
            update_string = ', '.join(update_list)
            query = "UPDATE users SET %s WHERE email = %%s" % update_string

            parameters_tuple = values_tuple + (email,)
            # Uncomment this line for debugging:
            # print('Query: ', query, '\nParameters tuple: ', parameters_tuple)
            cur.execute(query, parameters_tuple)


def delete_user(conn_info, email):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE email = %s", (email,))


def update_hash_code(conn_info, hash_code, email):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            hex_hash_code = format_hash_code(hash_code)
            cur.execute("UPDATE users SET hash_code = E%s WHERE email = %s", (hex_hash_code, email))


# Helper function for select_all_users and select_one_user that converts a data record from the cursor into a more
# useful, JSONify-able dictionary.
def get_dict_from_record(record):
    return {k: v for (k, v) in zip(('user_id', 'email') + DESIRED_FIELDS, (*record,))}


def select_all_users(conn_info):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT %s FROM users" % COLUMNS_TO_SELECT)
            records = cur.fetchall()
            return [get_dict_from_record(record) for record in records] if records else None


def select_one_user(conn_info, column, value):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT %s FROM users WHERE %s = %%s" % (COLUMNS_TO_SELECT, column), (value,))
            record = cur.fetchone()
            return get_dict_from_record(record) if record else None


def select_hash_code(conn_info, email):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hash_code FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            return row[0].tobytes() if row else None


def user_exists(conn_info, column, value):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT * FROM users WHERE %s = %%s)" % column, (value,))
            return cur.fetchone()[0]


def email_exists(conn_info, email):
    return user_exists(conn_info, 'email', email)


def get_conn(dbname, dbusername, dbpassword, dbhost, dbport):
    conn = psycopg2.connect(
        "dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (
            dbname, dbusername, dbpassword, dbhost, dbport))
    conn.autocommit = True
    return conn
