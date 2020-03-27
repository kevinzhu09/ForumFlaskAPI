DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS posts CASCADE;

-- Example table:
CREATE TABLE IF NOT EXISTS users (
	user_id SERIAL PRIMARY KEY,
	hash_code BYTEA NOT NULL,
	email VARCHAR (100) NOT NULL,
	username VARCHAR (20) NULL,
    verified BOOLEAN NOT NULL,
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    first_name VARCHAR (50) NULL,
    last_name VARCHAR (50) NULL
);
CREATE UNIQUE INDEX users_email_constraint ON users (email)
    WHERE verified;
CREATE UNIQUE INDEX users_username_constraint ON users (username)
    WHERE verified;


CREATE TABLE IF NOT EXISTS posts (
    post_id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES users (user_id),
    title VARCHAR (20) NOT NULL,
    content TEXT,
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE UNIQUE INDEX posts_author_title_constraint ON posts (author_id, title)
    WHERE NOT deleted;

SELECT * FROM users;
UPDATE users SET verified = TRUE WHERE verified = FALSE;
SELECT hash_code, user_id FROM users WHERE email = 'kevinzoolu@gmail.com' AND verified = TRUE;