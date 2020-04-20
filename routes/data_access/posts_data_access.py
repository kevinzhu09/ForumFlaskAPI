from routes.routes_config import get_conn, format_binary, conn_info


def insert_post(author_id, title, content):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_post(%s, %s, %s, NULL);", (author_id, title, content))
            return cur.fetchone()[0]


def insert_image(image_data, user_id, mime_type):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_image(E%s, %s, %s, NULL);", (format_binary(image_data), user_id, mime_type))
            return cur.fetchone()[0]


def select_image(image_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT image_data, mime_type FROM select_image(%s);", (image_id,))
            row = cur.fetchone()
            return {'image_data': row[0], 'mime_type': row[1]} if row[0] and row[1] else None


def liked_post_exists(post_id, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT exists_bool FROM liked_post_exists(%s,%s);", (post_id, user_id))
            return cur.fetchone()[0]


def insert_liked_post(post_id, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_liked_post(%s, %s);", (post_id, user_id))


def delete_liked_post(post_id, user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_liked_post(%s, %s);", (post_id, user_id))


def delete_post(post_id, author_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_post(%s, %s);", (post_id, author_id))


def update_post(content, post_id, author_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL update_post(%s, %s, %s);", (content, post_id, author_id))


def select_post_including_content(post_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT title, content, author_id, created_timestamp, username FROM select_post_including_content(%s);",
                (post_id,))
            post = cur.fetchone()
            return {k: v for (k, v) in
                    zip(('title', 'content', 'author_id', 'created_timestamp', 'username'), (*post,))} \
                if post[0] and post[1] and post[2] and post[3] and post[4] else None


def select_recent_posts():
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT post_id, author_id, title, username, created_timestamp FROM select_recent_posts();")
            posts = cur.fetchall()
            return [
                {k: v for (k, v) in zip(('post_id', 'author_id', 'title', 'username', 'created_timestamp'), (*post,))}
                for post in posts] if posts else None


def select_recent_posts_from_author(author_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT post_id, title, created_timestamp FROM select_recent_posts_from_author(%s);",
                        (author_id,))
            posts = cur.fetchall()
            posts = [{k: v for (k, v) in zip(('post_id', 'title', 'created_timestamp'), (*post,))} for post in
                     posts] if posts else None
            cur.execute("SELECT username FROM select_username(%s);", (author_id,))
            username = cur.fetchone()[0]
            return posts, username


def select_liked_posts(user_id):
    with get_conn(*conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT post_id, author_id, title, username, created_timestamp FROM select_liked_posts(%s);",
                        (user_id,))
            posts = cur.fetchall()
            return [
                {k: v for (k, v) in zip(('post_id', 'author_id', 'title', 'username', 'created_timestamp'), (*post,))}
                for post in posts] if posts else None
