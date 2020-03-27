# External modules: psycopg2 connects to the database. json loads .json files.
import psycopg2

from constants import POST_INFO_TO_SELECT


def insert_post(conn_info, author_id, title, content):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO posts (author_id, title, content) VALUES (%s, %s, %s)", (author_id, title, content))


def delete_post(conn_info, post_id, author_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE posts SET deleted = TRUE WHERE post_id = %s AND author_id = %s", (post_id, author_id))
            return cur.rowcount


def update_post(conn_info, post_id, author_id, content):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE posts SET content = %s WHERE post_id = %s AND author_id = %s AND deleted = FALSE", (content, post_id, author_id))
            return cur.rowcount


def select_post_content_and_author_id(conn_info, post_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT content, author_id FROM posts WHERE post_id = %s AND deleted = FALSE", (post_id,))
            return cur.fetchone()


def get_dict_from_post(post):
    return {k: v for (k, v) in zip(('post_id', 'user_name', 'title', 'created_timestamp'), (*post,))}


def select_recent_posts(conn_info):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT %s FROM posts FROM posts P INNER JOIN users U ON P.author_id = U.user_id WHERE deleted "
                        "= FALSE ORDER BY P.post_id DESC LIMIT 10" % POST_INFO_TO_SELECT)
            posts = cur.fetchall()
            return [get_dict_from_post(post) for post in posts] if posts else None


def select_recent_posts_from_author(conn_info, author_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT %s FROM posts FROM posts P INNER JOIN users U ON P.author_id = U.user_id WHERE deleted "
                        "= FALSE AND P.author_id = %%s ORDER BY P.post_id DESC LIMIT 10" % POST_INFO_TO_SELECT,
                        (author_id,))
            posts = cur.fetchall()
            return [get_dict_from_post(post) for post in posts] if posts else None


def get_conn(dbname, dbusername, dbpassword, dbhost, dbport):
    conn = psycopg2.connect(
        "dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (
            dbname, dbusername, dbpassword, dbhost, dbport))
    conn.autocommit = True
    return conn
