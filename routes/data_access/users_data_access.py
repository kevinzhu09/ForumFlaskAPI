from routes.routes_config import get_conn, format_binary, conn_info


def insert_regular_user(hash_code, email, username):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_regular_user(%s, E%s, %s, NULL);", (email, format_binary(hash_code), username))
            return cur.fetchone()[0]


def login_social_user(social_id, email, provider, username):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL login_social_user(%s, %s, %s, %s, NULL);", (social_id, email, provider, username))
            return cur.fetchone()[0]


def verify_regular_user(email, unverified_user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute('CALL verify_regular_user(%s, %s);', (email, unverified_user_id))


def delete_user(user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_user(%s);", (user_id,))


def update_regular_user_hash_code(hash_code, email=None, user_id=None):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            hex_hash_code = format_binary(hash_code)
            if user_id:
                cur.execute("CALL update_regular_user_hash_code_by_id(E%s, %s);",
                            (hex_hash_code, user_id))
            elif email:
                cur.execute("CALL update_regular_user_hash_code_by_email(E%s, %s, NULL);",
                            (hex_hash_code, email))
                return cur.fetchone()[0]
            else:
                raise TypeError('Neither email nor user_id were provided.')


def select_liked_authors(user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT author_id, username FROM select_liked_authors(%s);",
                (user_id,))
            authors = cur.fetchall()
            return [{'author_id': author[0], 'username': author[1]} for author in authors] if authors else None


def select_regular_user_hash_code_and_id(email):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hash_code, user_id FROM select_regular_user_hash_code_and_id(%s);", (email,))
            row = cur.fetchone()
            return (row[0].tobytes(), row[1]) if row[0] and row[1] else None


def select_unverified_regular_user_hash_code(email, unverified_user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hash_code FROM select_unverified_regular_user_hash_code(%s, %s);",
                        (email, unverified_user_id))
            row = cur.fetchone()
            return row[0].tobytes() if row[0] else None


def select_regular_user_hash_code(user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hash_code FROM select_regular_user_hash_code(%s);", (user_id,))
            row = cur.fetchone()
            return row[0].tobytes() if row[0] else None


def email_exists(email, social_login):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            if social_login:
                pass
            else:
                cur.execute("SELECT exists_bool FROM regular_user_email_exists(%s);", (email,))
                return cur.fetchone()[0]


def username_exists(username, social_login):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            if social_login:
                pass
            else:
                cur.execute("SELECT exists_bool FROM regular_user_username_exists(%s);", (username,))
                return cur.fetchone()[0]


def select_liked_author(author_id, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT exists_bool FROM select_liked_author(%s, %s);", (author_id, user_id))
            return cur.fetchone()[0]


def insert_liked_author(author_id, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_liked_author(%s, %s);", (author_id, user_id))


def delete_liked_author(author_id, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_liked_author(%s, %s);", (author_id, user_id))


def check_social_login(user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT social_login FROM check_social_login(%s);", (user_id,))
            return cur.fetchone()[0]

