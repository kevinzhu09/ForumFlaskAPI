-- insert_post
CREATE OR REPLACE PROCEDURE insert_post(IN author_id INTEGER, IN title VARCHAR (30), IN content TEXT, INOUT post_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
		
	INSERT INTO posts (author_id, title, content) VALUES (insert_post.author_id, insert_post.title, insert_post.content)
	RETURNING posts.post_id INTO insert_post.post_id;
	
    COMMIT;
END;
$$;
CALL insert_post(27, 'My Titl5', 'THIS IS MY CONTENT', NULL);
-- insert_image
CREATE OR REPLACE PROCEDURE insert_image(IN image_data BYTEA, IN user_id INTEGER, IN mime_type CHAR(4), INOUT image_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN 
	INSERT INTO images (image_data, user_id, mime_type) VALUES (insert_image.image_data, insert_image.user_id, insert_image.mime_type) 
	RETURNING images.image_id INTO insert_image.image_id;
    COMMIT;
END;
$$;
CALL insert_image(E'DEADBEEF', 27, 'png', NULL);
-- select_image
CREATE OR REPLACE FUNCTION select_image(IN image_id INTEGER, OUT image_data BYTEA, OUT mime_type CHAR(4))
AS $$
BEGIN
	SELECT images.image_data, images.mime_type INTO select_image.image_data, select_image.mime_type 
	FROM images WHERE images.image_id = select_image.image_id; 
END; $$

LANGUAGE plpgsql;

SELECT image_data, mime_type FROM select_image(5);
-- select_liked_post
CREATE OR REPLACE FUNCTION liked_post_exists(IN post_id INTEGER, IN user_id INTEGER, OUT exists_bool BOOLEAN)
AS $$
BEGIN
	SELECT EXISTS (SELECT * FROM liked_posts WHERE liked_posts.post_id = liked_post_exists.post_id 
				   AND liked_posts.user_id = liked_post_exists.user_id) INTO exists_bool;
END; $$

LANGUAGE plpgsql;

SELECT exists_bool FROM liked_post_exists(6,27);
-- insert_liked_post
CREATE OR REPLACE PROCEDURE insert_liked_post(IN post_id INTEGER, IN user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	INSERT INTO liked_posts (post_id, user_id) VALUES (insert_liked_post.post_id, insert_liked_post.user_id);
    COMMIT;
END;
$$;
CALL insert_liked_post(10,27);
-- delete_liked_post
CREATE OR REPLACE PROCEDURE delete_liked_post(IN post_id INTEGER, IN user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	DELETE FROM liked_posts WHERE liked_posts.post_id = delete_liked_post.post_id AND liked_posts.user_id = delete_liked_post.user_id;
    COMMIT;
END;
$$;
CALL delete_liked_post(2,27);
-- delete_post
CREATE OR REPLACE PROCEDURE delete_post(IN post_id INTEGER, IN author_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	UPDATE posts SET deleted = TRUE WHERE posts.post_id = delete_post.post_id AND posts.author_id = delete_post.author_id;
    COMMIT;
END;
$$;
CALL delete_post(6,27);
-- update_post
CREATE OR REPLACE PROCEDURE update_post(IN content TEXT, IN post_id INTEGER, IN author_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	UPDATE posts SET content = update_post.content WHERE posts.post_id = update_post.post_id 
	AND posts.author_id = update_post.author_id AND posts.deleted = FALSE;
    COMMIT;
END;
$$;
CALL update_post('Mu conent', 7, 27);
-- select_post_including_content
CREATE OR REPLACE FUNCTION select_post_including_content(IN post_id INTEGER, OUT title VARCHAR (30), OUT content TEXT,
														 OUT author_id INTEGER, OUT created_timestamp TIMESTAMP WITH TIME ZONE, OUT username VARCHAR (20))
AS $$
BEGIN

 SELECT P.title, P.content, P.author_id, P.created_timestamp,
  	CASE
		WHEN U.social_login = TRUE THEN
			SU.username
		ELSE
			RU.username
	END
 INTO select_post_including_content.title, 
 select_post_including_content.content, select_post_including_content.author_id, select_post_including_content.created_timestamp, 
 select_post_including_content.username
 FROM posts P INNER JOIN users U ON P.author_id = U.user_id
 LEFT JOIN social_login_users SU ON U.user_id = SU.user_id AND U.social_login = TRUE
 LEFT JOIN regular_login_users RU ON U.user_id = RU.user_id AND U.social_login = FALSE AND RU.verified = TRUE
 WHERE P.deleted = FALSE AND P.post_id = select_post_including_content.post_id;
 
END; $$

LANGUAGE plpgsql;

SELECT title, content, author_id, created_timestamp, username FROM select_post_including_content(3);
-- select_recent_posts
CREATE OR REPLACE FUNCTION select_recent_posts()
  RETURNS TABLE(post_id INTEGER, author_id INTEGER, title VARCHAR (30), username VARCHAR (20), 
				created_timestamp TIMESTAMP WITH TIME ZONE) AS $$
BEGIN
 RETURN QUERY
	SELECT P.post_id, P.author_id, P.title, 
  	CASE
		WHEN U.social_login = TRUE THEN
			SU.username
		ELSE
			RU.username
	END
	AS username,
	P.created_timestamp
	FROM posts P INNER JOIN users U ON P.author_id = U.user_id 
	LEFT JOIN social_login_users SU ON U.user_id = SU.user_id AND U.social_login = TRUE
	LEFT JOIN regular_login_users RU ON U.user_id = RU.user_id AND U.social_login = FALSE AND RU.verified = TRUE
	WHERE P.deleted = FALSE ORDER BY P.post_id DESC LIMIT 20;
END; $$

LANGUAGE plpgsql;

SELECT post_id, author_id, title, username, created_timestamp FROM select_recent_posts();
-- select_recent_posts_from_author
CREATE OR REPLACE FUNCTION select_recent_posts_from_author(IN author_id INTEGER)
  RETURNS TABLE(post_id INTEGER, title VARCHAR (30), 
				created_timestamp TIMESTAMP WITH TIME ZONE) AS $$
BEGIN
 RETURN QUERY
	SELECT P.post_id, P.title, P.created_timestamp
	FROM posts P INNER JOIN users U ON P.author_id = U.user_id 
	WHERE P.deleted = FALSE AND P.author_id = select_recent_posts_from_author.author_id ORDER BY P.post_id DESC LIMIT 20;
	
END; $$

LANGUAGE plpgsql;

SELECT post_id, title, created_timestamp, username FROM select_recent_posts_from_author(27);
-- select_username
CREATE OR REPLACE FUNCTION select_username(IN user_id INTEGER, OUT username VARCHAR (20))
AS $$
BEGIN
	SELECT
		CASE
			WHEN U.social_login = TRUE THEN
				SU.username
			ELSE
				RU.username
		END
		INTO select_username.username 
		FROM users U
		LEFT JOIN social_login_users SU ON U.user_id = SU.user_id AND U.social_login = TRUE
		LEFT JOIN regular_login_users RU ON U.user_id = RU.user_id AND U.social_login = FALSE AND RU.verified = TRUE
		WHERE U.user_id = select_username.user_id;
	END; $$

LANGUAGE plpgsql;

SELECT username FROM select_username(1);
-- select_liked_posts
CREATE OR REPLACE FUNCTION select_liked_posts(IN user_id INTEGER)
  RETURNS TABLE(post_id INTEGER, author_id INTEGER, title VARCHAR (30), username VARCHAR (20), 
				created_timestamp TIMESTAMP WITH TIME ZONE) AS $$
BEGIN
 RETURN QUERY
	SELECT P.post_id,
		P.author_id,
		P.title, 
  	CASE
		WHEN U.social_login = TRUE THEN
			SU.username
		ELSE
			RU.username
	END
	AS username,
	P.created_timestamp
	FROM liked_posts L 
	INNER JOIN posts P
		ON L.post_id = P.post_id 
	INNER JOIN users U
		ON P.author_id = U.user_id
	LEFT JOIN social_login_users SU
		ON U.user_id = SU.user_id AND U.social_login = TRUE
	LEFT JOIN regular_login_users RU
		ON U.user_id = RU.user_id AND U.social_login = FALSE AND RU.verified = TRUE
	WHERE P.deleted = FALSE AND L.user_id = select_liked_posts.user_id
	ORDER BY P.post_id DESC LIMIT 20;

END; $$

LANGUAGE plpgsql;

SELECT post_id, author_id, title, username, created_timestamp FROM select_liked_posts(27);


