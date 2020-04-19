-- noinspection SqlNoDataSourceInspectionForFile

-- use functions or stored procedures for all python code to make it simple
-- insert new user
-- insert regular user
DROP PROCEDURE insert_regular_user(IN email VARCHAR (50), IN hash_code BYTEA, IN username VARCHAR (20), INOUT user_id INTEGER);
CREATE OR REPLACE PROCEDURE insert_regular_user(IN email VARCHAR (50), IN hash_code BYTEA, IN username VARCHAR (20), INOUT user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	INSERT INTO users (social_login) VALUES (FALSE) RETURNING users.user_id INTO insert_regular_user.user_id;
    INSERT INTO regular_login_users (user_id, email, hash_code, username, verified) VALUES
		(insert_regular_user.user_id, insert_regular_user.email, insert_regular_user.hash_code, insert_regular_user.username, FALSE);
	
    COMMIT;
END;
$$;
CALL insert_regular_user('kevinzoolu@gmal.com', 'DEADBEEF', 'dracia', NULL);
CALL insert_regular_user('kevinzoolu@gmal.com', 'DEADBEEF', 'dracia');
-- insert social login user
CREATE OR REPLACE PROCEDURE login_social_user(social_id VARCHAR (255), IN email VARCHAR (50), 
											  IN provider social_login_provider, IN username VARCHAR (20), INOUT user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	SELECT social_login_users.user_id 
	INTO login_social_user.user_id
	FROM social_login_users 
	WHERE social_login_users.social_id = login_social_user.social_id AND social_login_users.provider = login_social_user.provider;
	IF login_social_user.user_id IS NULL THEN
		INSERT INTO users (social_login) VALUES (TRUE) RETURNING users.user_id INTO login_social_user.user_id;
		INSERT INTO social_login_users (user_id, social_id, email, provider, username) 
		VALUES (login_social_user.user_id, login_social_user.social_id, login_social_user.email,
				login_social_user.provider, login_social_user.username);
	END IF;
    COMMIT;
END;
$$;
CALL login_social_user('55334', 'k@gmail.com', 'Google', 'drao', NULL);
-- verify regular user
CREATE OR REPLACE PROCEDURE verify_regular_user(IN email VARCHAR (50), IN unverified_user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	UPDATE regular_login_users SET verified = TRUE WHERE regular_login_users.email = verify_regular_user.email AND 
		regular_login_users.verified = FALSE AND regular_login_users.user_id = verify_regular_user.unverified_user_id;
	
    COMMIT;
END;
$$;

CALL verify_regular_user('kevinzoolu@gmal.com', 27);
-- delete user
CREATE OR REPLACE PROCEDURE delete_user(IN user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN

	DELETE FROM liked_posts WHERE liked_posts.user_id = delete_user.user_id;
	DELETE FROM liked_authors WHERE liked_authors.user_id = delete_user.user_id;
	DELETE FROM posts WHERE posts.author_id = delete_user.user_id;
	DELETE FROM regular_login_users WHERE regular_login_users.user_id = delete_user.user_id AND verified = TRUE;
	DELETE FROM social_login_users WHERE social_login_users.user_id = delete_user.user_id;
	DELETE FROM users WHERE users.user_id = delete_user.user_id;

	COMMIT;
END;
$$;


CALL delete_user(27);
-- comments in between to split things up
-- functions for get requests/select
-- update_regular_user_hash_code by email and by id. split them up
-- update_regular_user_hash_code_by_id
CREATE OR REPLACE PROCEDURE update_regular_user_hash_code_by_id(IN hash_code BYTEA, IN user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	UPDATE regular_login_users SET hash_code = update_regular_user_hash_code_by_id.hash_code 
	WHERE regular_login_users.user_id = update_regular_user_hash_code_by_id.user_id AND regular_login_users.verified = TRUE;
	
    COMMIT;
END;
$$;

CALL update_regular_user_hash_code_by_id(E'DEADBEEF', 27);
-- update_regular_user_hash_code_by_email
CREATE OR REPLACE PROCEDURE update_regular_user_hash_code_by_email(IN hash_code BYTEA, IN email VARCHAR (50), INOUT user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	UPDATE regular_login_users SET hash_code = update_regular_user_hash_code_by_email.hash_code 
	WHERE regular_login_users.email = update_regular_user_hash_code_by_email.email AND regular_login_users.verified = TRUE
	RETURNING regular_login_users.user_id INTO update_regular_user_hash_code_by_email.user_id;
	
    COMMIT;
END;
$$;

CALL update_regular_user_hash_code_by_email(E'DEADBEEF', 'kevinzoolu@gmal.com', NULL);
-- select liked authors
DROP FUNCTION select_liked_authors();

CREATE OR REPLACE FUNCTION select_liked_authors(IN user_id INTEGER)
  RETURNS TABLE(author_id INTEGER, username VARCHAR (20)) AS $$
BEGIN
 RETURN QUERY

 SELECT L.author_id, 
 	CASE
		WHEN U.social_login = TRUE THEN
			SU.username
		ELSE
			RU.username
	END
	 AS username
 FROM liked_authors L INNER JOIN users U ON L.author_id = U.user_id
 LEFT JOIN social_login_users SU ON U.user_id = SU.user_id AND U.social_login = TRUE
 LEFT JOIN regular_login_users RU ON U.user_id = RU.user_id AND U.social_login = FALSE AND RU.verified = TRUE
 WHERE L.user_id = select_liked_authors.user_id;

END; $$

LANGUAGE plpgsql;

SELECT author_id, username FROM select_liked_authors(27);
-- select hash code and id
CREATE OR REPLACE FUNCTION select_regular_user_hash_code_and_id(IN email VARCHAR (50), OUT hash_code BYTEA,  OUT user_id INTEGER)
AS $$
BEGIN
 
 SELECT regular_login_users.hash_code, regular_login_users.user_id INTO select_regular_user_hash_code_and_id.hash_code, select_regular_user_hash_code_and_id.user_id 
 FROM regular_login_users WHERE regular_login_users.email = select_regular_user_hash_code_and_id.email AND regular_login_users.verified = TRUE;

END; $$

LANGUAGE plpgsql;
SELECT * FROM regular_login_users
SELECT hash_code, user_id FROM select_regular_user_hash_code_and_id('kevin.zhu@uconn.edu');

-- select_unverified_regular_user_hash_code
CREATE OR REPLACE FUNCTION select_unverified_regular_user_hash_code(IN email VARCHAR (50), IN unverified_user_id INTEGER, OUT hash_code BYTEA)
AS $$
BEGIN
 
 SELECT regular_login_users.hash_code INTO select_unverified_regular_user_hash_code.hash_code FROM regular_login_users WHERE regular_login_users.email = select_unverified_regular_user_hash_code.email 
 AND verified = FALSE AND user_id = unverified_user_id;
END; $$

LANGUAGE plpgsql;

SELECT hash_code FROM select_unverified_regular_user_hash_code('kevinzoolu@gmail.com', 3);
-- select_regular_user_hash_code
CREATE OR REPLACE FUNCTION select_regular_user_hash_code(IN user_id INTEGER, OUT hash_code BYTEA)
AS $$
BEGIN
 
 SELECT regular_login_users.hash_code INTO select_regular_user_hash_code.hash_code FROM regular_login_users 
 WHERE regular_login_users.user_id = select_regular_user_hash_code.user_id AND verified = TRUE;
END; $$

LANGUAGE plpgsql;

SELECT hash_code FROM select_regular_user_hash_code(27);
-- email exists
CREATE OR REPLACE FUNCTION regular_user_email_exists(IN email VARCHAR (50), OUT exists_bool BOOLEAN)
AS $$
BEGIN

 SELECT EXISTS (SELECT * FROM regular_login_users WHERE regular_login_users.email = regular_user_email_exists.email 
				AND verified = TRUE) INTO exists_bool;
END; $$

LANGUAGE plpgsql;

SELECT exists_bool FROM regular_user_email_exists('kevinzoolu@gmal.com');
-- username exists
CREATE OR REPLACE FUNCTION regular_user_username_exists(IN username VARCHAR (20), OUT exists_bool BOOLEAN)
AS $$
BEGIN

 SELECT EXISTS (SELECT * FROM regular_login_users WHERE regular_login_users.username = regular_user_username_exists.username 
				AND verified = TRUE) INTO exists_bool;
END; $$

LANGUAGE plpgsql;

SELECT exists_bool FROM regular_user_username_exists('dracia');
-- select_liked_author
CREATE OR REPLACE FUNCTION select_liked_author(IN author_id INTEGER, IN user_id INTEGER, OUT exists_bool BOOLEAN)
AS $$
BEGIN

 SELECT EXISTS (SELECT * FROM liked_authors WHERE liked_authors.author_id = select_liked_author.author_id 
				AND liked_authors.user_id = select_liked_author.user_id) INTO exists_bool;
END; $$

LANGUAGE plpgsql;

SELECT exists_bool FROM select_liked_author(5, 27);
-- insert_liked_author
CREATE OR REPLACE PROCEDURE insert_liked_author(IN author_id INTEGER, IN user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	INSERT INTO liked_authors (author_id, user_id) VALUES (insert_liked_author.author_id, insert_liked_author.user_id);
	
    COMMIT;
END;
$$;

CALL insert_liked_author(5,27);
-- delete_liked_author
CREATE OR REPLACE PROCEDURE delete_liked_author(IN author_id INTEGER, IN user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	DELETE FROM liked_authors WHERE liked_authors.author_id = delete_liked_author.author_id AND liked_authors.user_id = delete_liked_author.user_id;
    COMMIT;
END;
$$;

CALL delete_liked_author(5,27);
-- check_regular_user_verified_username
CREATE OR REPLACE FUNCTION check_regular_user_verified_username(IN user_id INTEGER, OUT username VARCHAR (20))
AS $$
BEGIN
SELECT
 	CASE
		WHEN U.social_login = TRUE THEN
			SU.username
		ELSE
			RU.username
	END
	FROM users U
 	LEFT JOIN social_login_users SU ON U.user_id = SU.user_id AND U.social_login = TRUE
 	LEFT JOIN regular_login_users RU ON U.user_id = RU.user_id AND U.social_login = FALSE AND RU.verified = TRUE
 WHERE U.user_id = check_regular_user_verified_username.user_id INTO check_regular_user_verified_username.username;
END; $$

LANGUAGE plpgsql;

SELECT username FROM check_regular_user_verified_username(8);
-- check_social_login
CREATE OR REPLACE FUNCTION check_social_login(IN user_id INTEGER, OUT social_login BOOLEAN)
AS $$
BEGIN
	SELECT users.social_login FROM users WHERE users.user_id = check_social_login.user_id INTO check_social_login.social_login;
END; $$

LANGUAGE plpgsql;

SELECT social_login FROM check_social_login(1);



