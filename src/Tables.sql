-- DATABASES PROJECT 2023

--Cláudia dos Reis Torres
--Daniel Ferreira Veiga
--Maria João Dutra Rosa


--TABLES

CREATE TABLE consumer (
	accountdate VARCHAR(512) NOT NULL,
	person_id	 INTEGER,
	PRIMARY KEY(person_id)
);

CREATE TABLE artist (
	artisticname	 VARCHAR(512) NOT NULL,
	admin_person_id INTEGER NOT NULL,
	person_id	 INTEGER,
	PRIMARY KEY(person_id)
);

CREATE TABLE admin (
	person_id INTEGER,
	PRIMARY KEY(person_id)
);

CREATE TABLE subscription (
	id_subs		 SERIAL,
	initial_date	 DATE NOT NULL,
	final_date	 DATE NOT NULL,
	consumer_person_id INTEGER NOT NULL,
	PRIMARY KEY(id_subs)
);

CREATE TABLE playlist (
	id_playlist	 SERIAL,
	name		 VARCHAR(512) NOT NULL,
	type		 VARCHAR(512) NOT NULL,
	consumer_person_id INTEGER NOT NULL,
	PRIMARY KEY(id_playlist)
);

CREATE TABLE song (
	ismn		 VARCHAR(13) NOT NULL,
	title		 VARCHAR(512) NOT NULL,
	genre		 VARCHAR(512) NOT NULL,
	duration	 VARCHAR(512) NOT NULL,
	releasedate	 DATE NOT NULL,
	publisherid	 INTEGER NOT NULL,
	label_id_label	 INTEGER NOT NULL,
	artist_person_id INTEGER NOT NULL,
	PRIMARY KEY(ismn)
);

CREATE TABLE label (
	id_label SERIAL,
	name	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(id_label)
);

CREATE TABLE album (
	id_album	 SERIAL,
	name		 VARCHAR(512) NOT NULL,
	releasedate	 DATE NOT NULL,
	artist_person_id INTEGER NOT NULL,
	PRIMARY KEY(id_album)
);

CREATE TABLE prepaidcards (
	id_card	 BIGINT,
	limitdate	 VARCHAR(512) NOT NULL,
	initialammount	 FLOAT(8) NOT NULL,
	amount		 FLOAT(8) NOT NULL,
	admin_person_id INTEGER NOT NULL,
	PRIMARY KEY(id_card)
);

CREATE TABLE person (
	id	 SERIAL,
	username VARCHAR(512) NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	password VARCHAR(512) NOT NULL,
	address	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE comment (
	id_comment	 SERIAL,
	comment		 VARCHAR(512),
	song_ismn		 VARCHAR(13) NOT NULL,
	consumer_person_id INTEGER NOT NULL,
	PRIMARY KEY(id_comment)
);

CREATE TABLE logs (
	id_log		 SERIAL,
	initial_date	 DATE NOT NULL,
	song_ismn		 VARCHAR(13),
	consumer_person_id INTEGER,
	PRIMARY KEY(id_log,song_ismn,consumer_person_id)
);

CREATE TABLE albumorder (
	order_type	 INTEGER,
	album_id_album INTEGER,
	song_ismn	 VARCHAR(13),
	PRIMARY KEY(order_type,album_id_album,song_ismn)
);

CREATE TABLE playlist_song (
	playlist_id_playlist INTEGER,
	song_ismn		 VARCHAR(13),
	PRIMARY KEY(playlist_id_playlist,song_ismn)
);

CREATE TABLE consumer_playlist (
	consumer_person_id	 INTEGER,
	playlist_id_playlist INTEGER,
	PRIMARY KEY(consumer_person_id,playlist_id_playlist)
);

CREATE TABLE prepaidcards_subscription (
	prepaidcards_id_card BIGINT,
	subscription_id_subs INTEGER,
	cost FLOAT(8) NOT NULL, --change: cost variable to store the subscription cost
	PRIMARY KEY(prepaidcards_id_card,subscription_id_subs)
);

CREATE TABLE artist_song (
	artist_person_id INTEGER,
	song_ismn	 VARCHAR(13),
	PRIMARY KEY(artist_person_id,song_ismn)
);

CREATE TABLE comment_comment (
	comment_id_comment	 INTEGER,
	parent_id_comment INTEGER NOT NULL, --change: variable name more intuitive
	PRIMARY KEY(comment_id_comment)
);

CREATE TABLE artist_label (
	artist_person_id INTEGER,
	label_id_label	 INTEGER,
	PRIMARY KEY(artist_person_id,label_id_label)
);

ALTER TABLE consumer ADD CONSTRAINT consumer_fk1 FOREIGN KEY (person_id) REFERENCES person(id);
ALTER TABLE artist ADD CONSTRAINT artist_fk1 FOREIGN KEY (admin_person_id) REFERENCES admin(person_id);
ALTER TABLE artist ADD CONSTRAINT artist_fk2 FOREIGN KEY (person_id) REFERENCES person(id);
ALTER TABLE admin ADD CONSTRAINT admin_fk1 FOREIGN KEY (person_id) REFERENCES person(id);
ALTER TABLE subscription ADD CONSTRAINT subscription_fk1 FOREIGN KEY (consumer_person_id) REFERENCES consumer(person_id);
ALTER TABLE playlist ADD CONSTRAINT playlist_fk1 FOREIGN KEY (consumer_person_id) REFERENCES consumer(person_id);
ALTER TABLE song ADD UNIQUE (publisherid);
ALTER TABLE song ADD CONSTRAINT song_fk1 FOREIGN KEY (label_id_label) REFERENCES label(id_label);
ALTER TABLE song ADD CONSTRAINT song_fk2 FOREIGN KEY (artist_person_id) REFERENCES artist(person_id);
ALTER TABLE album ADD CONSTRAINT album_fk1 FOREIGN KEY (artist_person_id) REFERENCES artist(person_id);
ALTER TABLE prepaidcards ADD CONSTRAINT prepaidcards_fk1 FOREIGN KEY (admin_person_id) REFERENCES admin(person_id);
ALTER TABLE person ADD UNIQUE (username, email);
ALTER TABLE comment ADD CONSTRAINT comment_fk1 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE comment ADD CONSTRAINT comment_fk2 FOREIGN KEY (consumer_person_id) REFERENCES consumer(person_id);
ALTER TABLE logs ADD CONSTRAINT logs_fk1 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE logs ADD CONSTRAINT logs_fk2 FOREIGN KEY (consumer_person_id) REFERENCES consumer(person_id);
ALTER TABLE albumorder ADD CONSTRAINT albumorder_fk1 FOREIGN KEY (album_id_album) REFERENCES album(id_album);
ALTER TABLE albumorder ADD CONSTRAINT albumorder_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE playlist_song ADD CONSTRAINT playlist_song_fk1 FOREIGN KEY (playlist_id_playlist) REFERENCES playlist(id_playlist);
ALTER TABLE playlist_song ADD CONSTRAINT playlist_song_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE consumer_playlist ADD CONSTRAINT consumer_playlist_fk1 FOREIGN KEY (consumer_person_id) REFERENCES consumer(person_id);
ALTER TABLE consumer_playlist ADD CONSTRAINT consumer_playlist_fk2 FOREIGN KEY (playlist_id_playlist) REFERENCES playlist(id_playlist);
ALTER TABLE prepaidcards_subscription ADD CONSTRAINT prepaidcards_subscription_fk1 FOREIGN KEY (prepaidcards_id_card) REFERENCES prepaidcards(id_card);
ALTER TABLE prepaidcards_subscription ADD CONSTRAINT prepaidcards_subscription_fk2 FOREIGN KEY (subscription_id_subs) REFERENCES subscription(id_subs);
ALTER TABLE artist_song ADD CONSTRAINT artist_song_fk1 FOREIGN KEY (artist_person_id) REFERENCES artist(person_id);
ALTER TABLE artist_song ADD CONSTRAINT artist_song_fk2 FOREIGN KEY (song_ismn) REFERENCES song(ismn);
ALTER TABLE comment_comment ADD CONSTRAINT comment_comment_fk1 FOREIGN KEY (comment_id_comment) REFERENCES comment(id_comment);
ALTER TABLE comment_comment ADD CONSTRAINT comment_comment_fk2 FOREIGN KEY (parent_id_comment) REFERENCES comment(id_comment);
ALTER TABLE artist_label ADD CONSTRAINT artist_label_fk1 FOREIGN KEY (artist_person_id) REFERENCES artist(person_id);
ALTER TABLE artist_label ADD CONSTRAINT artist_label_fk2 FOREIGN KEY (label_id_label) REFERENCES label(id_label);


--DATA

-- Insert data into 'person' table
INSERT INTO person (username, email, password, address)
VALUES ('john123', 'johnny@email.com', 'cGFzc3dvcmQxMjM=', '123 Main St'), --password123
       ('Emma_Brown', 'emma456@email.com', 'cGFzc3dvcmQ0NTY=', '456 Elm St'), --password456
       ('BrunoMars_Oficial', 'bruno_mars@email.com', 'Qm1hcnM=', '649 Back St'); --Bmars

-- Insert data into 'admin' table
INSERT INTO admin (person_id)
VALUES (1);

-- Insert data into 'consumer' table
INSERT INTO consumer (accountdate, person_id)
VALUES ('2023-05-01', 2);

-- Insert data into 'artist' table
INSERT INTO artist (artisticname, admin_person_id, person_id)
VALUES ('Bruno Mars', 1, 3);

-- Insert data into 'label' table
INSERT INTO label (name)
VALUES ('Star records'),
       ('Label Z');

-- Insert data into 'song' table
INSERT INTO song (ismn, title, genre, duration, releasedate, publisherid, label_id_label, artist_person_id)
VALUES ('1234567890123', 'Billionaire', 'Pop', '3:45', '2023-01-01', 1, 1, 3),
       ('9876543210987', 'The Lazy Song', 'Pop', '4:10', '2023-02-01', 3, 1, 3);

-- Insert data into 'subscription' table
INSERT INTO subscription (initial_date, final_date, consumer_person_id)
VALUES ('2023-05-01', '2024-05-01', 2);

-- Insert data into 'playlist' table
INSERT INTO playlist (name, type, consumer_person_id)
VALUES ('Top10', 'Personal', 2);

-- Insert data into 'album' table
INSERT INTO album (name, releasedate, artist_person_id)
VALUES ('First Album', '2023-03-01', 3);

-- Insert data into 'prepaidcards' table
INSERT INTO prepaidcards (id_card, limitdate, initialammount, amount, admin_person_id)
VALUES (8304672863962853, '2024-05-01', 50.00, 50.00, 1);

-- Insert data into 'comment' table
INSERT INTO comment (comment, song_ismn, consumer_person_id)
VALUES ('Great song!', '1234567890123', 2),
       ('Nice track!', '9876543210987', 2);

-- Insert data into 'logs' table
INSERT INTO logs (initial_date, song_ismn, consumer_person_id)
VALUES ('2023-05-01', '1234567890123', 2),
       ('2023-05-02', '9876543210987', 2);

-- Insert data into 'albumorder' table
INSERT INTO albumorder (order_type, album_id_album, song_ismn)
VALUES (1, 1, '1234567890123'),
       (2, 1, '9876543210987');

-- Insert data into 'playlist_song' table
INSERT INTO playlist_song (playlist_id_playlist, song_ismn)
VALUES (1, '1234567890123'),
       (1, '9876543210987');

-- Insert data into 'consumer_playlist' table
INSERT INTO consumer_playlist (consumer_person_id, playlist_id_playlist)
VALUES (2, 1);

-- Insert data into 'prepaidcards_subscription' table
INSERT INTO prepaidcards_subscription (prepaidcards_id_card, subscription_id_subs, cost)
VALUES (8304672863962853, 1, 7.0);

-- Insert data into 'artist_song' table
INSERT INTO artist_song (artist_person_id, song_ismn)
VALUES (3, '1234567890123'),
       (3, '9876543210987');

-- Insert data into 'comment_comment' table
INSERT INTO comment_comment (comment_id_comment, parent_id_comment)
VALUES (2, 1);

-- Insert data into 'artist_label' table
INSERT INTO artist_label (artist_person_id, label_id_label)
VALUES (3, 1);


--TRIGGER

-- Create function
CREATE OR REPLACE FUNCTION update_top_10_playlist()
RETURNS TRIGGER AS $$
DECLARE
    top_playlist_id INTEGER;
BEGIN
    -- Find the top 10 playlist ID for the consumer
    SELECT id_playlist
    INTO STRICT top_playlist_id
    FROM playlist
    WHERE consumer_person_id = NEW.consumer_person_id
    ORDER BY id_playlist
    LIMIT 1;

    -- Clear the current top 10 playlist for the consumer
    DELETE FROM playlist_song WHERE playlist_id_playlist = top_playlist_id;

    -- Insert the updated top 10 playlist for the consumer
    INSERT INTO playlist_song (playlist_id_playlist, song_ismn)
    SELECT top_playlist_id, song_ismn
    FROM (
        SELECT song_ismn, COUNT(*) AS play_count
        FROM logs
        WHERE consumer_person_id = NEW.consumer_person_id AND initial_date >= (current_date - interval '30 days') -- Filter logs from the last 30 days
        GROUP BY song_ismn
        ORDER BY COUNT(*) DESC
        LIMIT 10
    ) AS top_songs;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER update_top_10_trigger
AFTER INSERT ON logs
FOR EACH ROW
EXECUTE FUNCTION update_top_10_playlist();