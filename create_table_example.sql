DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;

-- Example table:
CREATE TABLE IF NOT EXISTS users (
	user_id SERIAL PRIMARY KEY,
	hash_code BYTEA NOT NULL,
	email VARCHAR (100) UNIQUE NOT NULL,
    verified BOOLEAN NOT NULL,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    first_name VARCHAR (50) NULL,
    last_name VARCHAR (50) NULL,
    phone_number VARCHAR (20) NULL
);

CREATE TABLE IF NOT EXISTS posts (
    post_id SERIAL PRIMARY KEY,
    user_id INTEGER FOREIGN KEY REFERENCES users (user_id),
    title VARCHAR (20),
    content TEXT,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
