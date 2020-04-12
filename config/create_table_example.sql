DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS posts CASCADE;

-- Example table:
CREATE TABLE IF NOT EXISTS users (
	user_id SERIAL PRIMARY KEY,
	hash_code BYTEA NOT NULL,
	email VARCHAR (50) NOT NULL,
	username VARCHAR (20) NULL,
    verified BOOLEAN NOT NULL,
    created_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    first_name VARCHAR (30) NULL,
    last_name VARCHAR (30) NULL
);
CREATE UNIQUE INDEX users_email_constraint ON users (email)
    WHERE verified;
CREATE UNIQUE INDEX users_username_constraint ON users (username)
    WHERE verified;


CREATE TABLE IF NOT EXISTS posts (
    post_id SERIAL PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES users (user_id),
    title VARCHAR (30) NOT NULL,
    content TEXT,
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
	image_data bytea NOT NULL,
	image_name VARCHAR(20) NOT NULL,
	mime_type CHAR(4) NOT NULL
);

CREATE OR REPLACE PROCEDURE delete_user(INT)
LANGUAGE plpgsql    
AS $$
BEGIN

	DELETE FROM liked_posts WHERE user_id = $1;
	DELETE FROM liked_authors WHERE user_id = $1;
	DELETE FROM posts WHERE author_id = $1;
	DELETE FROM users WHERE user_id = $1 AND verified = TRUE;

	COMMIT;

END;
$$;


CALL delete_user(3);

SELECT * FROM users;
SELECT * FROM posts;
SELECT * FROM liked_posts;
SELECT * FROM liked_authors;
UPDATE users SET verified = TRUE WHERE verified = FALSE AND user_id = 22;
SELECT hash_code, user_id FROM users WHERE email = 'kevinzoolu@gmail.com' AND verified = TRUE;

-- populate the users table:
INSERT INTO users (hash_code, email, username, verified, first_name, last_name) VALUES
(E'ABCABC', 'john@john.com', 'john', TRUE, 'John', 'Frederick');
INSERT INTO users (hash_code, email, username, verified, first_name, last_name) VALUES
(E'ABCABC', 'josh@john.com', 'josh', TRUE, 'Josh', 'Frederick');
INSERT INTO users (hash_code, email, username, verified, first_name, last_name) VALUES
(E'ABCABC', 'drew@john.com', 'drew', TRUE, 'Drew', 'Frederick');

-- populate posts table:
INSERT INTO posts (author_id, title, content) VALUES
(4, 'The Greatest Post', 'A young honey bee named Barry B. Benson (Jerry Seinfeld) has recently graduated from college and is about to enter the hives Honex Industries honey-making workforce alongside his best friend Adam Flayman (Matthew Broderick). Barry is initially excited to join the workforce, but his courageous, non-conformist attitude emerges upon discovering that his choice of job will never change once picked. Later, the two bees run into a group of Pollen Jocks, bees who collect pollen from flowers outside the hive. The Jocks offer to take Barry outside the hive to a flower patch, and he accepts. While on his first pollen-gathering expedition in New York City, Barry gets lost in the rain, and ends up on the balcony of a human florist named Vanessa (Renée Zellweger). Upon noticing Barry, Vanessas boyfriend Ken (Patrick Warburton) attempts to squash him, but Vanessa gently catches and releases Barry outside the window, saving his life.

Barry later returns to express his gratitude to Vanessa, breaking the sacred rule that bees are not supposed to communicate with humans. Barry and Vanessa develop a close bond, bordering on attraction, and spend time together frequently. Later, while Barry and Vanessa are walking through a grocery store, Barry is horrified to discover that the humans have been stealing and eating the bees honey for centuries. He decides to journey to Honey Farms, which supplies the grocery store with its honey. Furious at the poor treatment of the bees in the hive, including the use of bee smokers to subdue the colony, Barry decides to sue the human race to put an end to the exploitation of bees.

Barrys mission attracts wide attention from bees and humans alike, and hundreds of people show up to watch the trial. Although Barry is up against tough defense attorney Layton T. Montgomery (John Goodman) the trials first day goes well. That evening, Barry is having dinner with Vanessa when Ken shows up. Vanessa leaves the room, and Ken expresses to Barry that he hates the pair spending time together. When Barry leaves to use the restroom, Ken ambushes Barry and attempts to kill him, only for Vanessa to intervene and break up with Ken. The next day at the trial, Montgomery unleashes an unrepentant character assassination against the bees leading a deeply offended Adam to sting him; Montgomery immediately exaggerates the stinging to make himself appear the victim of an assault while simultaneously denouncing Adam. Adams actions jeopardize the bees credibility and put his life in danger, though he manages to survive. While visiting Adam in the hospital, Barry notices two people smoking outside, and is struck by inspiration. The next day, Barry wins the trial by exposing the jury to the cruel treatment bees are subjected to, particularly the smoker, and humans are banned from stealing honey from bees ever again.

Having lost the trial, Montgomery cryptically warns Barry that a negative shift in the balance of nature is imminent. As it turns out, the sudden, massive stockpile of honey has put every bee out of a job, including the vitally important Pollen Jocks. As a result, without anything to pollinate them, all of the worlds plant life slowly begins to die out. Before long, the last remaining flowers on Earth are being stockpiled in Pasadena, California for what is expected to be the final Tournament of Roses Parade. Barry and Vanessa travel to the parade and steal a parade float, which they load onto a plane to be delivered to the bees so they can re-pollinate the worlds flowers. When the planes pilot and copilot are knocked unconscious, Vanessa is forced to land the plane, with help from Barry and the bees from Barrys hive.

Armed with the pollen of the last flowers, Barry and the Pollen Jocks manage to reverse the damage and save the worlds flowers, restarting the bees honey production. Humans and bees are seen working together, and certain brands of honey are now "bee-approved". Barry becomes a member of the Pollen Jocks, helping to pollinate the worlds plants. Barry is also seen running a law firm inside Vanessas flower shop, titled "Insects at Law", handling disputes between animals and humans. Ken is not pleased with this discovery as Andy (Chuck Martin) tells him to let it go. The film ends with Barry flying off to a flower patch with the Pollen Jocks.');

INSERT INTO posts (author_id, title, content) VALUES
(5, 'How to Dance', 'The primary uses of dance notation are historical dance preservation through documentation, and analysis (e.g., in ethnochoreology) or reconstruction of choreography, dance forms, and technical exercises. Also, dance notation allows a dance work to be documented and therefore potentially copyrighted.');

INSERT INTO posts (author_id, title, content) VALUES
(6, 'This Week in Movies', 'My favorite movies are Captain America: The First Avenger
Iron Man
The Incredible Hulk
Iron Man 2
Thor
The Avengers
Iron Man 3
Thor: The Dark World
Captain America: The Winter Soldier
Guardians of the Galaxy
Guardians of the Galaxy Vol. 2
Avengers: Age of Ultron
Ant-Man
Captain America: Civil War
Spider-Man: Homecoming
Doctor Strange
Thor: Ragnarok
Black Panther
Avengers: Infinity War
Ant-Man and the Wasp
Captain Marvel');

DROP FUNCTION get_all_users();

CREATE OR REPLACE FUNCTION get_all_users()
  RETURNS TABLE(_userId INTEGER, _email VARCHAR, _username VARCHAR) AS $$
BEGIN
 RETURN QUERY
 
 SELECT user_id, email, username FROM users WHERE verified = TRUE;

END; $$
 
LANGUAGE plpgsql;

SELECT get_all_users();

SELECT * FROM users;

DROP PROCEDURE insert(VARCHAR, VARCHAR, VARCHAR);
CREATE OR REPLACE PROCEDURE insert(VARCHAR, VARCHAR, VARCHAR)
LANGUAGE plpgsql    
AS $$
BEGIN
    INSERT INTO users (hash_code, email, username, verified, first_name, last_name) VALUES
(E'ABCABC', 'user1@john.com', $1, TRUE, 'John', 'Frederick');
INSERT INTO users (hash_code, email, username, verified, first_name, last_name) VALUES
(E'ABCABC', 'user2@john.com', $2, TRUE, 'Josh', 'Frederick');
INSERT INTO users (hash_code, email, username, verified, first_name, last_name) VALUES
(E'ABCABC', 'user3@john.com', $3, TRUE, 'Drew', 'Frederick');
    
 
    COMMIT;
END;
$$;


CALL insert('usera','userb','userc');

