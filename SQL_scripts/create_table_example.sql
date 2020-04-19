-- noinspection SqlNoDataSourceInspectionForFile

DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS regular_login_users CASCADE;
DROP TABLE IF EXISTS social_login_users CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS images CASCADE;
DROP TABLE IF EXISTS liked_posts CASCADE;
DROP TABLE IF EXISTS liked_authors CASCADE;

-- Create the tables:
CREATE TABLE IF NOT EXISTS users (
	user_id SERIAL PRIMARY KEY,
	social_login BOOLEAN NOT NULL,
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);



CREATE TABLE IF NOT EXISTS regular_login_users (
	user_id INTEGER NOT NULL REFERENCES users (user_id) PRIMARY KEY,
	email VARCHAR (50) NOT NULL,
	hash_code BYTEA NOT NULL,
    username VARCHAR (20) NULL,
    verified BOOLEAN NOT NULL
);

CREATE UNIQUE INDEX regular_login_users_email_constraint ON regular_login_users (email)
    WHERE verified;
CREATE UNIQUE INDEX regular_login_users_username_constraint ON regular_login_users (username)
    WHERE verified;

CREATE TYPE social_login_provider AS ENUM ('Google', 'Twitter');

CREATE TABLE IF NOT EXISTS social_login_users (
	user_id INTEGER NOT NULL REFERENCES users (user_id) PRIMARY KEY,
	social_id VARCHAR (255) NOT NULL,
	email VARCHAR (50) NOT NULL,
	provider social_login_provider NOT NULL,
	username VARCHAR (20) NULL,
	UNIQUE (social_id, provider)
);

CREATE TABLE IF NOT EXISTS posts (
    post_id SERIAL PRIMARY KEY,
    title VARCHAR (30) NOT NULL,
    content TEXT,
    author_id INTEGER NOT NULL REFERENCES users (user_id),
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE UNIQUE INDEX posts_author_title_constraint ON posts (author_id, title)
    WHERE NOT deleted;

CREATE TABLE IF NOT EXISTS liked_posts (
    post_id INTEGER NOT NULL REFERENCES posts (post_id),
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (post_id, user_id)
);

CREATE TABLE IF NOT EXISTS liked_authors (
    author_id INTEGER NOT NULL REFERENCES users (user_id),
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (author_id, user_id)
);

CREATE TABLE IF NOT EXISTS images (
	image_id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES users (user_id),
	image_data BYTEA NOT NULL,
	image_name VARCHAR(20) NOT NULL,
	mime_type CHAR(4) NOT NULL
);
