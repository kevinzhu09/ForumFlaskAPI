-- Example table:
CREATE TABLE IF NOT EXISTS users (
        user_id serial PRIMARY KEY,
	    hash_code bytea NOT NULL,
	    email VARCHAR (100) UNIQUE NOT NULL,
        first_name VARCHAR (50) NULL,
        last_name VARCHAR (50) NULL,
        phone_number VARCHAR (20) NULL
        );
		