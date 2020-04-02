# External modules: psycopg2 connects to the database. json loads .json files.
import psycopg2

from constants import POSTS_INFO_TO_SELECT, POSTS_KEYS, SINGLE_POST_INFO_TO_SELECT, SINGLE_POST_KEYS, \
    AUTHOR_POST_INFO_TO_SELECT, AUTHOR_POST_KEYS


def insert_post(conn_info, author_id, title, content):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO posts (author_id, title, content) VALUES (%s, %s, %s) RETURNING post_id",
                        (author_id, title, content))
            return cur.fetchone()[0]


def select_like(conn_info, post_id, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT * FROM likes WHERE post_id = %s AND user_id = %s)", (post_id, user_id))
            return cur.fetchone()[0]


def insert_like(conn_info, post_id, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO likes (post_id, user_id) VALUES (%s, %s)", (post_id, user_id))


def delete_like(conn_info, post_id, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))


def delete_post(conn_info, post_id, author_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE posts SET deleted = TRUE WHERE post_id = %s AND author_id = %s", (post_id, author_id))
            return cur.rowcount


def update_post(conn_info, post_id, author_id, content):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE posts SET content = %s WHERE post_id = %s AND author_id = %s AND deleted = FALSE",
                        (content, post_id, author_id))
            return cur.rowcount


def get_dict_from_post(post, keys):
    return {k: v for (k, v) in zip(keys, (*post,))}


def select_post_including_content(conn_info, post_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT %s FROM posts P INNER JOIN users U ON P.author_id = U.user_id WHERE deleted = FALSE AND post_id = %%s" % SINGLE_POST_INFO_TO_SELECT,
                (post_id,))
            post = cur.fetchone()
            return get_dict_from_post(post, SINGLE_POST_KEYS) if post else None


def select_recent_posts(conn_info):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT %s FROM posts P INNER JOIN users U ON P.author_id = U.user_id WHERE deleted "
                        "= FALSE ORDER BY P.post_id DESC LIMIT 10" % POSTS_INFO_TO_SELECT)
            posts = cur.fetchall()
            return [get_dict_from_post(post, POSTS_KEYS) for post in posts] if posts else None


def select_recent_posts_from_author(conn_info, author_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT %s FROM posts WHERE deleted = FALSE AND author_id = %%s ORDER BY post_id DESC LIMIT 10" % AUTHOR_POST_INFO_TO_SELECT,
                (author_id,))
            posts = cur.fetchall()
            post_dict = [get_dict_from_post(post, AUTHOR_POST_KEYS) for post in posts] if posts else None
            cur.execute("SELECT username FROM users WHERE verified = TRUE AND user_id = %s", (author_id,))
            username = cur.fetchone()
            return post_dict, username


def select_liked_posts(conn_info, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT %s FROM likes L INNER JOIN posts P ON L.post_id = P.post_id INNER JOIN users U ON P.author_id = U.user_id WHERE P.deleted = FALSE AND L.user_id = %%s" % POSTS_INFO_TO_SELECT, (user_id,))
            posts = cur.fetchall()
            return [get_dict_from_post(post, POSTS_KEYS) for post in posts] if posts else None


def check_verified(conn_info, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username FROM users WHERE user_id = %s AND verified = TRUE", (user_id,))
            return cur.fetchone()[0]


def get_conn(dbname, dbusername, dbpassword, dbhost, dbport):
    conn = psycopg2.connect(
        "dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (
            dbname, dbusername, dbpassword, dbhost, dbport))
    conn.autocommit = True
    return conn
