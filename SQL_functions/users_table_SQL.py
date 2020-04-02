# External modules: psycopg2 connects to the database. json loads .json files.
import psycopg2

from constants import DESIRED_FIELDS, FIELDS_LENGTH, COLUMNS_TO_SELECT, COLUMNS_TO_INSERT


# Helper function for insert_user and update_hash_code.
def format_hash_code(hash_code):
    hex_hash_code = "\\\\x" + hash_code.hex()
    return hex_hash_code


def insert_user(*values_tuple, conn_info, hash_code, email, username):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            query = "INSERT INTO users (%s) VALUES (E%%s, %sFALSE) RETURNING user_id" % (COLUMNS_TO_INSERT, '%s, ' * FIELDS_LENGTH)

            parameters_tuple = (format_hash_code(hash_code), email, username) + values_tuple
            # Uncomment this line for debugging:
            print('Query: ', query, '\nParameters tuple: ', parameters_tuple)
            cur.execute(query, parameters_tuple)
            return cur.fetchone()[0]


def verify_user(conn_info, email, unverified_user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            query = ("UPDATE users SET verified = TRUE WHERE email = %s AND verified = FALSE AND user_id = %s")
            parameters_tuple = (email, unverified_user_id)
            # Uncomment this line for debugging:
            print('Query: ', query, '\nParameters tuple: ', parameters_tuple)
            cur.execute(query, parameters_tuple)
            return cur.rowcount


def update_user(*values_tuple, conn_info, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            update_list = [("%s = %%s" % item) for item in DESIRED_FIELDS]
            update_string = ', '.join(update_list)
            query = "UPDATE users SET %s WHERE user_id = %%s AND verified = TRUE" % update_string

            parameters_tuple = values_tuple + (user_id,)
            # Uncomment this line for debugging:
            # print('Query: ', query, '\nParameters tuple: ', parameters_tuple)
            cur.execute(query, parameters_tuple)
            return cur.rowcount


def delete_user(conn_info, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE user_id = %s AND verified = TRUE", (user_id,))
            return cur.rowcount


def update_hash_code(conn_info, hash_code, email=None, user_id=None):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            hex_hash_code = format_hash_code(hash_code)
            if user_id:
                cur.execute("UPDATE users SET hash_code = E%s WHERE user_id = %s AND verified = TRUE",
                            (hex_hash_code, user_id))
            elif email:
                cur.execute("UPDATE users SET hash_code = E%s WHERE email = %s AND verified = TRUE",
                            (hex_hash_code, email))
            else:
                raise TypeError('Neither email nor user_id were provided.')
            return cur.rowcount


# Helper function for select_all_users and select_one_user that converts a data record from the cursor into a more
# useful, JSONify-able dictionary.


def get_dict_from_record(record):
    return {k: v for (k, v) in zip(('user_id', 'email', 'username') + DESIRED_FIELDS, (*record,))}


def select_all_users(conn_info):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT %s FROM users WHERE verified = TRUE" % COLUMNS_TO_SELECT)
            records = cur.fetchall()
            return [get_dict_from_record(record) for record in records] if records else None


def select_one_user(conn_info, column, value):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT %s FROM users WHERE %s = %%s AND verified = TRUE" % (COLUMNS_TO_SELECT, column),
                        (value,))
            record = cur.fetchone()
            return get_dict_from_record(record) if record else None


def select_hash_code_and_id(conn_info, email):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hash_code, user_id FROM users WHERE email = %s AND verified = TRUE", (email,))
            row = cur.fetchone()
            return (row[0].tobytes(), row[1]) if row else None


def select_hash_code_from_unverified(conn_info, email, unverified_user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hash_code FROM users WHERE email = %s AND verified = FALSE AND user_id = %s", (email, unverified_user_id))
            row = cur.fetchone()
            return row[0].tobytes() if row else None


def select_hash_code(conn_info, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hash_code FROM users WHERE user_id = %s AND verified = TRUE", (user_id,))
            row = cur.fetchone()
            return row[0].tobytes() if row else None


def user_exists(conn_info, column, value):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT * FROM users WHERE %s = %%s AND verified = TRUE)" % column, (value,))
            return cur.fetchone()[0]


def email_exists(conn_info, email):
    return user_exists(conn_info, 'email', email)


def username_exists(conn_info, username):
    return user_exists(conn_info, 'username', username)


def get_conn(dbname, dbusername, dbpassword, dbhost, dbport):
    conn = psycopg2.connect(
        "dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (
            dbname, dbusername, dbpassword, dbhost, dbport))
    conn.autocommit = True
    return conn
