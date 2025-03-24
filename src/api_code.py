## =============================================

## ================= Databases =================
## ============== LEI  2022/2023 ===============
## ================== Project ==================

## Department of Informatics Engineering
## University of Coimbra

## TEAM:
## Cláudia dos Reis Torres
## Daniel Ferreira Veiga
## Maria João Dutra Rosa
## =============================================

#IMPORTS
import flask
import logging
import psycopg2

import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
import base64
import random

#To call an endpoint:
import requests

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user='postgres',
        password='postgres',
        host='127.0.0.1',
        port='5432',
        database='dbfichas'
    )

    return db

##########################################################
## ENDPOINTS
##########################################################

@app.route('/')
def landing_page():
    return """

    Hello World (Python Native)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2022 Team<br/>
    <br/>
    """

##########################################################
## GENERATE TOKEN

#Define the secret key
app.config['SECRET_KEY'] = 'db2023' #databases 2023

def generate_token(user_id):
    #Set the expiration time for the token - 1h
    expiration = datetime.utcnow() + timedelta(hours=1)

    #Create the payload containing the user information
    payload = {
        'user_id': user_id,
        'exp': expiration
    }

    #Generate the JWT token using the secret key
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    return token

##########################################################
## ENCODE PASSWORD

def encode_password(password):
    #Encode users password for safety purposes
    encoded_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')
    return encoded_password

##########################################################
## VERIFICATIONS
## Functions return: error JSON response if NOT VALID | None if VALID

#Check if the body exists
def check_request_body():
    if not request.json:
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'Endpoint body missing.',
            'results': None
        }
        return jsonify(response)

#Check if arguments are all present
def check_required_arguments(arguments):
    if any(arg not in request.json for arg in arguments):
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'Wrong arguments.',
            'results': None
        }
        return jsonify(response)

#Check number of arguments
def check_number_of_arguments(num_expected):
    json_data = request.json
    num_arguments = len(json_data)

    if num_arguments != num_expected:
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'Incorrect number of arguments.',
            'results': None
        }
        return jsonify(response)

#Check if values inserted
def check_values(values):

    #Check if values are strings
    for value in values:
        if not isinstance(value, str):
            response = {
                'status': StatusCodes['api_error'],
                'errors': 'Please insert all values inside quote marks.',
                'results': None
            }
            return jsonify(response)

    #Check if values are not null
    if any(not value.strip() for value in values):
        #strip() takes off any white spaces before checking
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'You must insert information in all fields.',
            'results': None
        }
        return jsonify(response)

    #Check for sql injections
    for value in values:
        for SQLcommand in ["--", '\'', '"']:
            if SQLcommand in value:
                response = {
                    'status': StatusCodes['api_error'],
                    'errors': 'Invalid characters spotted.',
                    'results': None
                }
                return jsonify(response)

#Check date format
def date_format(string):
    if not (len(string) == 10 and string[4] == "-" and string[7] == "-" and string[:4].isdigit() and string[5:7].isdigit() and string[8:].isdigit()):
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'Incorrect date format, please insert: YYYY-MM-DD.',
            'results': None
        }
        return jsonify(response)

#Check email format
def email_format(email):
    if '@' in email and '.' in email:
        a_index = email.index('@')
        dot_index = email.index('.')
        if a_index < dot_index:
            return True
    return False

#Check duration format
def duration_format(string):
    if ':' in string:
        first_part, second_part = string.split(':')
        if first_part.isdigit() and second_part.isdigit():
            return True
    return False

#Check if token is valid - returns user_id if VALID
def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        return user_id
    except jwt.ExpiredSignatureError:
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'Expired token.',
            'results': None
        }
        return jsonify(response)
    except jwt.InvalidTokenError:
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'Invalid token.',
            'results': None
        }
        return jsonify(response)

#Check if user is an admin
def check_admin(user_id):
    cursor = db_connection().cursor()
    cursor.execute("SELECT * FROM admin WHERE person_id = %s", (user_id,))
    result = cursor.fetchone()
    if result is None:
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'User does not have admin permissions.',
            'results': None
        }
        return jsonify(response)

#Check if user is an artist
def check_artist(user_id):
    cursor = db_connection().cursor()
    cursor.execute("SELECT * FROM artist WHERE person_id = %s", (user_id,))
    result = cursor.fetchone()
    if result is None:
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'User does not have artist permissions.',
            'results': None
        }
        return jsonify(response)

#Check if user is a consumer
def check_consumer(user_id):
    cursor = db_connection().cursor()
    cursor.execute("SELECT * FROM consumer WHERE person_id = %s", (user_id,))
    result = cursor.fetchone()
    if result is None:
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'You must be a consumer.',
            'results': None
        }
        return jsonify(response)

##########################################################
## USER REGISTRATION

# POST http://localhost:8080/dbproj/user
# users: {"username": username, "email": email, "password": password, "address": address}
# admins: {"username": username, "email": email, "password": password, "address": address, "artistic_name": artistic_name, "token": token}

@app.route('/dbproj/user', methods=['POST'])
def register_user():

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    #:= used for a variable assignment inside an expression

    if 'token' in request.json:
        if (check_n_args := check_number_of_arguments(6)) is not None: return check_n_args
    else:
        if (check_n_args := check_number_of_arguments(4)) is not None: return check_n_args

    if (check_args_result := check_required_arguments(['username', 'email', 'password', 'address'])) is not None: return check_args_result

    #Extract information from the request body - - -

    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    address = request.json.get('address')

    #Check values
    if (check_values_result := check_values([username, email, password, address])) is not None: return check_values_result
    if email_format(email) is False: return jsonify({'status': 401, 'errors': 'Please insert a valid email format.', 'results': None })

    #Check if username already exists
    cursor = db_connection().cursor()
    cursor.execute("SELECT id FROM person WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result is not None:
        #If he found a user with that username
        response = {
            'status': 401,
            'errors': 'Invalid username: already exists.',
            'results': None
        }
        return jsonify(response)

    #Encode password
    encoded_password = encode_password(password)

    #Check if there's a token argument
    if 'token' in request.json:

        #There is: adding an artist - - -

        #Check if any parameter is missing
        if (check_args_result := check_required_arguments(['artistic_name'])) is not None: return check_args_result

        artistic_name = request.json.get('artistic_name')
        token = request.json.get('token')

        #Check if values
        if (check_values_result := check_values([artistic_name, token])) is not None: return check_values_result

        #Verify token
        admin_id = verify_token(token)
        if not isinstance(admin_id, int): return admin_id

        #Check if it's an admin
        if (result := check_admin(admin_id)) is not None: return result

        #Add the person
        cursor.execute("INSERT INTO person (username, email, password, address) VALUES (%s, %s, %s, %s) RETURNING id", (username, email, encoded_password, address))
        user_id = cursor.fetchone()[0]

        #Add the person to artist table
        cursor.execute("INSERT INTO artist (artisticname, admin_person_id, person_id) VALUES (%s, %s, %s)", (artistic_name, admin_id, user_id))

    else:

        #There is not: adding a consumer - - -

        #Add the person
        cursor.execute("INSERT INTO person (username, email, password, address) VALUES (%s, %s, %s, %s) RETURNING id", (username, email, encoded_password, address))
        user_id = cursor.fetchone()[0]

        #Add the person to the consumer table
        account_date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO consumer (accountdate, person_id) VALUES (%s, %s)", (account_date, user_id))

        #Create the "Top10" playlist
        cursor.execute("INSERT INTO playlist (name, type, consumer_person_id) VALUES ('Top10', 'Private', %s) RETURNING id_playlist", (user_id,))
        id_playlist = cursor.fetchone()[0]

        #Insert the playlist
        cursor.execute("INSERT INTO consumer_playlist (consumer_person_id, playlist_id_playlist) VALUES (%s, %s)", (user_id, id_playlist))

    #Commit
    cursor.execute("commit;")
    cursor.close()

    #Return response
    response = {
        'status': 200,
        'errors': None,
        'results': {'user_id': user_id}
    }
    return jsonify(response)

##########################################################
## USER AUTHENTICATION

# PUT http://localhost:8080/dbproj/user
# {"username": username, "password": password}

@app.route('/dbproj/user', methods=['PUT'])
def authenticate_user():

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(2)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['username', 'password'])) is not None: return check_args_result

    #Extract information from the request body - - -

    username = request.json.get('username')
    password = request.json.get('password')

    #Check values
    if (check_values_result := check_values([username, password])) is not None: return check_values_result

    #Encode password
    encoded_password = encode_password(password)

    #Perform user authentication
    cursor = db_connection().cursor()
    cursor.execute("SELECT id FROM person WHERE username = %s AND password = %s", (username, encoded_password))
    result = cursor.fetchone()

    #Authentication failed
    if result is None:
        response = {
            'status': 401,
            'errors': 'Invalid credentials.',
            'results': None
        }
        return jsonify(response)

    #Authentication didn't fail
    user_id = result[0]

    #Commit
    cursor.execute("commit;")
    cursor.close()

    #Generate a JWT token - - -
    token = generate_token(user_id)

    #Return the response
    response = {
        'status': 200,
        'errors': None,
        'results': {'auth_token': token}
    }
    return jsonify(response)

##########################################################
## ADD SONG

# POST http://localhost:8080/dbproj/song
# {"ismn": ismn, "title": title, "genre": genre, "duration": duration, "release_date": release_date, "label_id": label_id, "other_artists": [artist_id1, artist_id2,...], "token": token}

@app.route('/dbproj/song', methods=['POST'])
def add_song():

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(8)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['ismn', 'title', 'genre', 'duration', 'release_date', 'label_id', 'other_artists', 'token'])) is not None: return check_args_result

    #Extract information from the request body - - -

    ismn = request.json.get('ismn')
    title = request.json.get('title')
    genre = request.json.get('genre')
    duration = request.json.get('duration')
    release_date = request.json.get('release_date')
    label_id = request.json.get('label_id')
    other_artists = request.json.get('other_artists')
    token = request.json.get('token')

    #Check values
    if (check_values_result := check_values([ismn, title, genre, duration, release_date, label_id, token])) is not None: return check_values_result
    #Check the date format
    if (check_value_format := date_format(release_date)) is not None: return check_value_format
    #Check duration
    if duration_format(duration) is False: return jsonify({'status': 401, 'errors': 'Please insert a valid duration format.', 'results': None})
    #Check label id
    if label_id.isdigit() is False: return jsonify({'status': 401, 'errors': 'Please insert a valid label id.', 'results': None})

    #If "other_artists" is not empty do checks
    if other_artists:
        if isinstance(other_artists, list):
            if (check_values_result := check_values(other_artists)) is not None: return check_values_result
        else:
            response = {
                'status': 401,
                'errors': 'Invalid value: other_artists must be a list (full or empty).',
                'results': None
            }
            return jsonify(response)

    #Verify token
    artist_id = verify_token(token)
    if not isinstance(artist_id, int): return artist_id

    #Check if it's an artist
    if (result := check_artist(artist_id)) is not None: return result

    #More checks - - -
    cursor = db_connection().cursor()

    #Check if ismn already exists
    cursor.execute("SELECT ismn FROM song WHERE ismn = %s", (ismn,))
    result = cursor.fetchone()
    if result is not None: return jsonify({'status': 401, 'errors': 'Invalid ismn: must be an unique identifier.', 'results': None })

    # Check if label exists
    cursor.execute("SELECT * FROM label WHERE id_label = %s", (label_id,))
    result = cursor.fetchone()
    if result is None: return jsonify({'status': 401, 'errors': 'Invalid label.', 'results': None})

    # Check if other artists exist and if they are not repeated
    other_artists_temp=[]

    if other_artists:
        for art in other_artists:
            try:
                art= int(art)
            except ValueError:
                return jsonify({'status': 401, 'errors': 'Please put only numbers on the ids (on other_artists).', 'results': None})

            if art == artist_id: return jsonify({'status': 401, 'errors': 'Please dont insert your id (on other_artists).', 'results': None})
            if art in other_artists_temp: return jsonify({'status': 401, 'errors': 'Please dont insert repeated ids (on other_artists).', 'results': None})

            cursor.execute("SELECT person_id FROM artist WHERE person_id = %s", (art,))
            result = cursor.fetchone()
            if result is None: return jsonify({'status': 401, 'errors': 'Invalid artist id (on other_artis).', 'results': None})
            other_artists_temp.append(art)

    #Add song - - -
    cursor.execute(
        "INSERT INTO song (ismn, title, genre, duration, releasedate, publisherid, label_id_label, artist_person_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (ismn, title, genre, duration, release_date, artist_id, label_id, artist_id))

    #Insert into artist-song
    cursor.execute("INSERT INTO artist_song (artist_person_id, song_ismn) VALUES (%s, %s)", (artist_id, ismn))

    #Associate artist to label - if not already associated
    cursor.execute("INSERT INTO artist_label (artist_person_id, label_id_label) SELECT %s, %s WHERE NOT EXISTS (SELECT %s FROM artist_label WHERE artist_person_id = %s AND label_id_label = %s)",
                   (artist_id, label_id, label_id, artist_id, label_id))

    # Associate to other artists - if there are other artists to associate
    if other_artists:
        for artist_id in other_artists:
            cursor.execute("INSERT INTO artist_song (artist_person_id, song_ismn) VALUES (%s, %s)", (artist_id, ismn))

    #Commit
    cursor.execute("commit;")
    cursor.close()

    #Return the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
        'results': {'song_id': ismn}
    }
    return jsonify(response)

##########################################################
## ADD ALBUM

# POST http://localhost:8080/dbproj/album
# {"name": album_name, "release_date": date, "songs": [{"ismn": ismn, "title": title, "genre": genre, "duration": duration, "release_date": release_date, "label_id": label_id, "other_artists": [artist_id1, artist_id2, ...]}, existing_song_ismn, ...], "order_type": order_type, "token": "token" }

@app.route('/dbproj/album', methods=['POST'])
def add_album():

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(5)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['name', 'release_date', 'songs', 'order_type', 'token'])) is not None: return check_args_result

    #Extract information from the request body - - -

    album_name = request.json.get('name')
    release_date = request.json.get('release_date')
    songs = request.json.get('songs')
    order_type = request.json.get('order_type')
    token = request.json.get('token')

    #Check values
    if (check_values_result := check_values([album_name, release_date, order_type, token])) is not None: return check_values_result
    #Check the date format
    if (check_value_format := date_format(release_date)) is not None: return check_value_format
    #Check order type
    try:
        order_type = int(order_type)
    except ValueError:
        return jsonify({'status': 401, 'errors': 'Order type must be a number.', 'results': None})
    if not(order_type in [1, 2, 3]): return jsonify({'status': 401, 'errors': 'Order types available: 1- default | 2- by title | 3- by song duration.', 'results': None})

    #Verify token
    artist_id = verify_token(token)
    if not isinstance(artist_id, int): return artist_id

    #Check if it's an artist
    if (result := check_artist(artist_id)) is not None: return result

    #Check if songs is empty
    cursor = db_connection().cursor()
    songs_to_add= []

    if not songs:
        return jsonify({'status': 403, 'errors': 'Please insert songs.', 'results': None})
    else:
        #If it is not
        for song_data in songs:
            # If it's an existing song
            if isinstance(song_data, str):
                if (check_values_result := check_values([song_data])) is not None: return check_values_result

                #Check if the song exists
                cursor.execute("SELECT ismn FROM song WHERE ismn = %s", (song_data,))
                result = cursor.fetchone()
                if result is None: return jsonify({'status': 401, 'errors': 'Song not found: invalid ismn.', 'results': None})

                #Check if the song belongs to the artist
                cursor.execute("SELECT * FROM song WHERE ismn = %s AND artist_person_id = %s", (song_data, artist_id))
                result = cursor.fetchone()
                if result is None: return jsonify({'status': 401, 'errors': 'Songs must belong to the artist.', 'results': None})

                songs_to_add.append(song_data)
            #If it's not an existing song
            elif isinstance(song_data, dict):
                #Add token to song info
                song_data['token']= token

                #Add song
                url = 'http://localhost:8080/dbproj/song'
                response = requests.post(url, json=song_data)

                response_data = response.json()
                if response_data['status'] == 200:
                    songs_to_add.append(song_data['ismn'])
                else:
                    return jsonify(response_data)
            else:
                return jsonify({'status': 403, 'errors': 'Please insert only: an existing song ismn (between quotes) or a new song info (between braces).', 'results': None})

    #Create album
    cursor.execute("INSERT INTO album (name, releasedate, artist_person_id) VALUES (%s, %s, %s) RETURNING id_album", (album_name, release_date, artist_id))
    album_id = cursor.fetchone()[0]

    #Insert songs into the album
    for song in songs_to_add:
        cursor.execute("INSERT INTO albumorder (order_type, album_id_album, song_ismn) VALUES (%s, %s, %s)", (order_type, album_id, song))

    #Commit
    cursor.execute("commit;")
    cursor.close()

    #Return the response
    response = {
        'status': 200,
        'errors': None,
        'results': {'album_id': album_id}
    }
    return jsonify(response)

##########################################################
## SEARCH SONG

# GET http://localhost:8080/dbproj/song/{keyword}
# {"token": token}

@app.route('/dbproj/song/<string:keyword>', methods=['GET'])
def search_song(keyword):

    # Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(1)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['token'])) is not None: return check_args_result

    # Extract information from the request body - - -
    token = request.json.get('token')

    # Check values
    if (check_values_result := check_values([keyword, token])) is not None: return check_values_result

    # Verify token
    user_id = verify_token(token)
    if not isinstance(user_id, int): return user_id

    #Retrieve songs containing the keyword
    cursor = db_connection().cursor()

    cursor.execute("""
        SELECT song.title, artist.artisticname, albumorder.album_id_album
        FROM song
        JOIN artist_song ON song.ismn = artist_song.song_ismn
        JOIN artist ON artist_song.artist_person_id = artist.person_id
        LEFT JOIN albumorder ON song.ismn = albumorder.song_ismn
        WHERE song.title ILIKE %s;""", ('%' + keyword + '%',))

    #SQL QUERY:
    # 1- Select the infos we want: song title, artist name and albums id
    # 2- Our base table is "song"
    # 3- Inner join the table "song" with the table "artist_song" if the songs ismn matches (basically we get the table "song" with the 2 columns from the table "artist_song")
    #    (we can get duplicate songs on the "song" table part since the table "artist_song" can link the same song to multiple artists) = WE GET THE ARTISTS IDS
    # 4- Inner join the table "artist_table" with the table "artist" if the artist_song.artist_id = artist.person_id (now we have the artistic name associated with the artists)
    #    (basically we did join with the "artist" table on the "artist_song" table and then with the "artist_song" table on the "song" table) = WE GET THE ARTISTIC NAMES
    # 5- Left join on the "song" table with the "albumorder" table where the song ismn matches
    #    (we use left join so that if we don't have an associated album we get a null value instead of taking off the song record) = WE GET THE ALBUM IDS
    # 6- We only want the data for the song titles that contain the keyword (searched with ILIKE -> does the same as LIKE but its case-insensitive)

    results = cursor.fetchall()
    cursor.close()

    #Format the results (because we get repeated values)
    formatted_results = []
    for row in results:
        song_title, artist_name, album_id = row[:3]

        #Check if the song is in formatted_results
        existing_song = next((song for song in formatted_results if song["title"] == song_title), None)

        if existing_song:
            #Check if the artist name is not present
            if artist_name not in existing_song["artists"]:
                existing_song["artists"].append(artist_name)

            #Check if the album ID is not present
            if album_id is not None and album_id not in existing_song["albums"]:
                existing_song["albums"].append(album_id)
        else:
            #Create a new song entry
            formatted_results.append({
                "title": song_title,
                "artists": [artist_name],
                "albums": [album_id] if album_id is not None else []
            })

    #Return the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
        'results': formatted_results
    }
    return jsonify(response)

##########################################################
## DETAIL ARTIST

# GET http://localhost:8080/dbproj/artist_info/{artist_id}
# {"token": token}

@app.route('/dbproj/artist_info/<int:artist_id>', methods=['GET'])
def get_artist_info(artist_id):

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(1)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['token'])) is not None: return check_args_result

    #Extract information from the request body - - -
    token = request.json.get('token')

    #Check values
    if (check_values_result := check_values([token])) is not None: return check_values_result

    #Verify token
    user_id = verify_token(token)
    if not isinstance(user_id, int): return user_id

    cursor = db_connection().cursor()

    #Check if the artist id is valid
    if check_artist(artist_id) is not None: return jsonify({'status': 401, 'errors': 'Artist id invalid: doesnt belong to an artist.', 'results': None})

    #Retrieve artist details
    cursor.execute("""
            SELECT artist.artisticname, artist_song.song_ismn, albumorder.album_id_album, playlist_song.playlist_id_playlist
            FROM artist
            JOIN artist_song ON artist.person_id = artist_song.artist_person_id
            LEFT JOIN albumorder ON artist_song.song_ismn = albumorder.song_ismn
            LEFT JOIN playlist_song ON artist_song.song_ismn = playlist_song.song_ismn
            LEFT JOIN playlist ON playlist_song.playlist_id_playlist = playlist.id_playlist --left join da table playlist= type das playlists
            WHERE artist.person_id = %s AND (playlist.type = 'Public' OR playlist.type IS NULL)""", (artist_id,))

    # SQL QUERY:
    # 1- Select the infos we want: artist name, song ids, album ids and public playlist ids
    # 2- Our base table is "artist"
    # 3- Inner join the table "artist" with the table "artist_song" if the person_id matches = WE GET ALL SONG ISMNs FROM THE ARTIST
    # 4- Left join the table "albumorder" = WE GET ALL ALBUM IDS WHERE THE SONGS ARE
    # 5- Left join the table "playlist_song" = WE GET ALL PLAYLIST IDS WHERE THE SONGS ARE
    # 6- Left join the table "playlist" = WE GET THE TYPE OF THE PLAYLISTS
    # 7- We only want the data for the given artist id (artist.person_id = %s) and we only want the playlists that are not 'Private'

    results = cursor.fetchall()
    cursor.close()

    #Format the results (because we get repeated values)
    formatted_results = []
    for row in results:
        artist_name, song_ismn, album_id, playlist_id = row[:4]

        #Check if the artist is already in the formatted results
        existing_artist = next((artist for artist in formatted_results if artist["name"] == artist_name), None)

        if existing_artist:
            #Check if the song is not already in the artist's songs
            if song_ismn not in existing_artist["songs"]:
                existing_artist["songs"].append(song_ismn)

            #Check if the album ID is not already in the artist's albums
            if album_id is not None and album_id not in existing_artist["albums"]:
                existing_artist["albums"].append(album_id)

            #Check if the playlist ID is not already in the artist's playlists
            if playlist_id is not None and playlist_id not in existing_artist["playlists"]:
                existing_artist["playlists"].append(playlist_id)
        else:
            #Create a new entry for the artist
            formatted_results.append({
                "name": artist_name,
                "songs": [song_ismn],
                "albums": [album_id] if album_id is not None else [],
                "playlists": [playlist_id] if playlist_id is not None else []
            })

    #Return the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
        'results': formatted_results
    }
    return jsonify(response)

##########################################################
## SUBSCRIBE TO PREMIUM

# POST http://localhost:8080/dbproj/subscription
# {"period": "month" | "quarter" | "semester", "cards": [card_number1, ...], "token": token}

@app.route('/dbproj/subscription', methods=['POST'])
def subscribe_to_premium():

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(3)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['period', 'cards', 'token'])) is not None: return check_args_result

    #Extract information from the request body - - -

    period = request.json.get('period')
    cards = request.json.get('cards')
    token = request.json.get('token')

    #Check values
    if (check_values_result := check_values([period, token])) is not None: return check_values_result
    if period not in ["month", "quarter", "semester"]: return jsonify({'status': StatusCodes['api_error'], 'errors': 'Invalid subscription period, must be: month, quarter or semester.', 'results': None})

    if not cards:
        return jsonify({'status': 403, 'errors': 'Please insert cards.', 'results': None})
    else:
        if (check_values_result := check_values(cards)) is not None: return check_values_result

    #Verify token
    user_id = verify_token(token)
    if not isinstance(user_id, int): return user_id

    #Check if it's a consumer
    if (result := check_consumer(user_id)) is not None: return result

    #Calculate the subscription cost based on the period
    subscription_cost = calculate_subscription_cost(period)

    cursor = db_connection().cursor()

    #Check cards
    money=0
    cards_available=[]

    for c in cards:
        try:
            c = int(c)
        except ValueError:
            return jsonify({'status': 401, 'errors': 'Please put only numbers on the card numbers.', 'results': None})

        #Check if card exists
        cursor.execute("SELECT * FROM prepaidcards WHERE id_card = %s", (c,))
        result = cursor.fetchone()
        if result is None: return jsonify({'status': 401, 'errors': 'Card not found.', 'results': None})

        #Check if cards has been used by another consumer (a card can be used multiple times but always by the same consumer)
        cursor.execute("""
            SELECT subscription.consumer_person_id
            FROM prepaidcards_subscription
            JOIN subscription ON prepaidcards_subscription.subscription_id_subs = subscription.id_subs
            WHERE prepaidcards_subscription.prepaidcards_id_card = %s;
        """, (c,))
        result = cursor.fetchone()

        if result is not None and user_id not in result: return jsonify({'status': 401, 'errors': 'Card already used by another consumer.', 'results': None})

        #Check if card has enough money
        cursor.execute("SELECT amount FROM prepaidcards WHERE id_card = %s", (c,))
        card_value = cursor.fetchone()[0]

        if card_value >= subscription_cost:
            #Has enough money
            money=1
            cards_available.append([c,card_value])

    #Check if there's at least one card with enough money
    if money == 0: return jsonify({'status': 401, 'errors': 'Not enough money in the cards.', 'results': None})

    card_to_use= cards_available[0][0]
    card_value_to_use= cards_available[0][1]

    #Check if the consumer has an active subscription
    cursor.execute("SELECT final_date FROM subscription WHERE consumer_person_id = %s  ORDER BY id_subs DESC", (user_id,))
    result = cursor.fetchone()

    if result is not None and result[0] > datetime.now().date():
        #Consumer has an active subscription - new subscription period it's going to be at the end of the current one
        subscription_start_date= result[0]
        subscription_end_date = result[0] + calculate_timedelta(period)
    else:
        #Consumer does not have an active subscription - start the new subscription period from today
        subscription_start_date = datetime.now().date()
        subscription_end_date = datetime.now().date() + calculate_timedelta(period)

    #Store the subscription information/transaction details

    #Subscription
    cursor.execute("INSERT INTO subscription (initial_date, final_date, consumer_person_id) VALUES (%s, %s, %s) RETURNING id_subs", (subscription_start_date, subscription_end_date, user_id))
    subscription_id = cursor.fetchone()[0]

    #Associate subscription with card
    cursor.execute("INSERT INTO prepaidcards_subscription (prepaidcards_id_card, subscription_id_subs, cost) VALUES (%s, %s, %s)", (card_to_use, subscription_id, subscription_cost))

    #Deduct the subscription cost from the card's balance
    updated_card_value = card_value_to_use - subscription_cost
    cursor.execute("UPDATE prepaidcards SET amount = %s WHERE id_card = %s", (updated_card_value, card_to_use))

    #Commit
    cursor.execute("commit;")
    cursor.close()

    #Return the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
        'results': {'subscription_id': subscription_id}
    }
    return jsonify(response)

#Helper function to calculate the time based on the subscription period
def calculate_timedelta(period):
    if period == "month":
        return timedelta(days=30)
    elif period == "quarter":
        return timedelta(days=90)
    elif period == "semester":
        return timedelta(days=180)

#Helper function to calculate the subscription cost based on the period
def calculate_subscription_cost(period):
    subscription_costs = {
        "month": 7,
        "quarter": 21,
        "semester": 42
    }
    return subscription_costs[period]

##########################################################
## CREATE PLAYLIST

# POST http://localhost:8080/dbproj/playlist
# {"playlist_name": name, "visibility": "Public" | "Private", "songs": [song_ismn, ...], "token": token}

# Endpoint to create a playlist
@app.route('/dbproj/playlist', methods=['POST'])
def create_playlist():

    # Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(4)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['playlist_name', 'visibility', 'songs', 'token'])) is not None: return check_args_result

    # Extract information from the request body - - -

    playlist_name = request.json.get('playlist_name')
    visibility = request.json.get('visibility')
    songs = request.json.get('songs')
    token = request.json.get('token')

    # Check values
    if (check_values_result := check_values([playlist_name, visibility,  token])) is not None: return check_values_result
    if visibility not in ["Public", "Private"]: return jsonify({'status': StatusCodes['api_error'], 'errors': 'Please input either Public or Private on visibility.', 'results': None})

    if not songs:
        return jsonify({'status': 403, 'errors': 'Please insert songs.', 'results': None})
    else:
        if (check_values_result := check_values(songs)) is not None: return check_values_result

    #Check if the songs exist
    cursor = db_connection().cursor()
    for s in songs:
        cursor.execute("SELECT ismn FROM song WHERE ismn = %s", (s,))
        result = cursor.fetchone()
        if result is None: return jsonify({'status': 401, 'errors': 'Song not found: invalid ismn.', 'results': None})

    #Verify token
    user_id = verify_token(token)
    if not isinstance(user_id, int): return user_id

    #Check if it's a consumer
    if (result := check_consumer(user_id)) is not None: return result

    #Check if the user is a premium consumer - has an active subscription
    cursor.execute("SELECT final_date FROM subscription WHERE consumer_person_id = %s  ORDER BY id_subs DESC", (user_id,))
    result = cursor.fetchone()

    if not(result is not None and result[0] > datetime.now().date()):
        #Consumer does not have an active subscription
        return jsonify({'status': 401, 'errors': 'You must be premium to create playlists.', 'results': None})

    #Insert the playlist into the database
    cursor.execute("INSERT INTO playlist (name, type, consumer_person_id) VALUES (%s, %s, %s) RETURNING id_playlist", (playlist_name, visibility, user_id))
    id_playlist = cursor.fetchone()[0]

    #Insert the songs into the playlist_song table
    for song_id in songs:
        cursor.execute("INSERT INTO playlist_song (playlist_id_playlist, song_ismn) VALUES (%s, %s)", (id_playlist, song_id))

    #Commit
    cursor.execute("commit;")
    cursor.close()

    #Return the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
        'results': {'playlist_id': id_playlist}
    }
    return jsonify(response)

##########################################################
## PLAY SONG

# PUT http://localhost:8080/dbproj/song/{ismn}
# {"token": token}

@app.route('/dbproj/song/<string:ismn>', methods=['PUT'])
def play_song(ismn):

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(1)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['token'])) is not None: return check_args_result

    #Extract information from the request body - - -
    token = request.json.get('token')

    #Check values
    if (check_values_result := check_values([ismn, token])) is not None: return check_values_result

    #Check if the song exists
    cursor = db_connection().cursor()
    cursor.execute("SELECT ismn FROM song WHERE ismn = %s", (ismn,))
    result = cursor.fetchone()
    if result is None: return jsonify({'status': 401, 'errors': 'Song not found: invalid ismn.', 'results': None})

    #Verify token
    user_id = verify_token(token)
    if not isinstance(user_id, int): return user_id

    #Check if it's a consumer
    if (result := check_consumer(user_id)) is not None: return result

    #Store the played song in the logs table
    cursor.execute("INSERT INTO logs (initial_date, song_ismn, consumer_person_id) VALUES (%s, %s, %s) RETURNING id_log",(datetime.now().date(), ismn, user_id))

    #Commit
    cursor.execute("commit;")
    cursor.close()

    #Return the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
    }
    return jsonify(response)

#Top 10 playlist trigger:

#1
"""
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
"""

#2
"""
CREATE TRIGGER update_top_10_trigger
AFTER INSERT ON logs
FOR EACH ROW
EXECUTE FUNCTION update_top_10_playlist();
"""

##########################################################
## GENERATE PRE-PAID CARDS

# POST http://localhost:8080/dbproj/card
# {"number_cards": number, "card_price": 10 | 25 | 50, "token": token}

@app.route('/dbproj/card', methods=['POST'])
def generate_cards():

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(3)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['number_cards', 'card_price', 'token'])) is not None: return check_args_result

    #Extract information from the request body - - -
    number_cards = request.json.get('number_cards')
    card_price = request.json.get('card_price')
    token = request.json.get('token')

    #Check values
    if (check_values_result := check_values([number_cards, card_price, token])) is not None: return check_values_result
    if card_price not in ["10", "25", "50"]: return jsonify({'status': StatusCodes['api_error'], 'errors': 'Invalid card price, must be: 10, 25 or 50.', 'results': None})
    card_price = int(card_price)

    try:
        number_cards = int(number_cards)
    except ValueError:
        return jsonify(
            {'status': 401, 'errors': 'Please put only numbers on number_cards.', 'results': None})

    #Verify token
    admin_id = verify_token(token)
    if not isinstance(admin_id, int): return admin_id

    #Check if it's an admin
    if (result := check_admin(admin_id)) is not None: return result

    #Set card limit date to a year from now
    one_year_from_now = datetime.now() + timedelta(days=365)
    limit_date = one_year_from_now.strftime("%Y-%m-%d")

    #Generate the specified number of pre-paid cards
    cursor = db_connection().cursor()
    card_ids = []

    for i in range(number_cards):
        #Generate card ID
        while True:
            min_card_id = 10 ** 15  #Minimum 16-digit number
            max_card_id = (10 ** 16) - 1  #Maximum 16-digit number

            card_id = random.randint(min_card_id, max_card_id)

            #Check if the generated card ID already exists in the prepaid cards table
            cursor.execute("SELECT id_card FROM prepaidcards WHERE id_card = %s", (card_id,))
            result = cursor.fetchone()
            if result is None:
                #The generated card ID is unique
                break

        #Store the card information
        cursor.execute("INSERT INTO prepaidcards (id_card, limitdate, initialammount, amount, admin_person_id) VALUES (%s, %s, %s, %s, %s)", (card_id, limit_date, card_price, card_price, admin_id))

        #Put on the returning list
        card_ids.append(card_id)

    #Commit
    cursor.execute("commit;")
    cursor.close()

    #Return the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
        'results': {'card_ids': card_ids}
    }
    return jsonify(response)

##########################################################
## LEAVE COMMENT/FEEDBACK

# POST http://localhost:8080/dbproj/comments/{song_id}
# POST http://localhost:8080/dbproj/comments/{song_id}/{parent_comment_id} (if replying to an existing comment)
# {"comment": comment_details, "token": token}

@app.route('/dbproj/comments/<string:song_id>', methods=['POST'])
@app.route('/dbproj/comments/<string:song_id>/<int:parent_comment_id>', methods=['POST'])
def leave_comment(song_id, parent_comment_id=None):

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(2)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['comment', 'token'])) is not None: return check_args_result

    #Extract information from the request body - - -
    comment = request.json.get('comment')
    token = request.json.get('token')

    #Check values
    if (check_values_result := check_values([song_id, comment, token])) is not None: return check_values_result

    #Check if song exists
    cursor = db_connection().cursor()
    cursor.execute("SELECT ismn FROM song WHERE ismn = %s", (song_id,))
    result = cursor.fetchone()
    if result is None: return jsonify({'status': 401, 'errors': 'Song not found: invalid ismn.', 'results': None})

    #Check if parent_comment_id exists
    if parent_comment_id:
        cursor.execute("SELECT id_comment FROM comment WHERE id_comment = %s", (parent_comment_id,))
        result = cursor.fetchone()
        if result is None:
            return jsonify({'status': 401, 'errors': 'Parent comment not found.', 'results': None})
        else:
            # Check if parent_comment_id corresponds to the song_ismn
            cursor.execute("SELECT song_ismn FROM comment WHERE id_comment = %s", (parent_comment_id,))
            result = cursor.fetchone()
            if result[0] != song_id: return jsonify({'status': 401, 'errors': 'Parent comment doesnt match the song id.', 'results': None})

    #Verify token
    user_id = verify_token(token)
    if not isinstance(user_id, int): return user_id

    #Check if it's a consumer
    if (result := check_consumer(user_id)) is not None: return result

    #Insert the comment into the 'comment' table
    cursor = db_connection().cursor()
    cursor.execute("INSERT INTO comment (comment, song_ismn, consumer_person_id) VALUES (%s, %s, %s) RETURNING id_comment", (comment, song_id, user_id))
    comment_id = cursor.fetchone()[0]

    #If replying to an existing comment, insert into the 'comment_comment' table
    if parent_comment_id:
        cursor.execute("INSERT INTO comment_comment (comment_id_comment, parent_id_comment) VALUES (%s, %s)", (comment_id, parent_comment_id))

    #Commit
    cursor.execute("commit;")
    cursor.close()

    #Return the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
        'results': {'comment_id': comment_id}
    }
    return jsonify(response)

##########################################################
## GENERATE A MONTHLY REPORT

# GET http://localhost:8080/dbproj/report/{year-month}
# {"token": token}

@app.route('/dbproj/report/<string:year_month>', methods=['GET'])
def monthly_report(year_month):

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(1)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['token'])) is not None: return check_args_result

    # Extract information from the request body - - -
    token = request.json.get('token')

    # Check values
    if (check_values_result := check_values([year_month, token])) is not None: return check_values_result

    #Verify token
    user_id = verify_token(token)
    if not isinstance(user_id, int): return user_id

    #Check year-month format
    if len(year_month) == 7 and year_month[4] == "-" and year_month[:4].isdigit() and year_month[5:].isdigit():
        year_month= year_month + "-01"
    else:
        return jsonify({'status': StatusCodes['api_error'], 'errors': 'Incorrect format, please insert it like: YEAR-MONTH.', 'results': None})

    #Convert year_month to a datetime object
    try:
        year_month = datetime.strptime(year_month, '%Y-%m-%d')
    except ValueError:
        return jsonify({'status': StatusCodes['api_error'], 'errors': 'YEAR or MONTH not valid.', 'results': None})

    #Calculate the start date for the past 12 months
    start_date = year_month.replace(year=year_month.year - 1)

    #Generate monthly report
    cursor = db_connection().cursor()
    cursor.execute("""
        SELECT TO_CHAR(date_trunc('month', logs.initial_date), 'YYYY-MM') AS month, song.genre, COUNT(*) AS number_plays
        FROM logs
        JOIN song ON logs.song_ismn = song.ismn
        WHERE logs.initial_date >= %s AND logs.initial_date <= %s
        GROUP BY month, song.genre
        ORDER BY month, song.genre;""", (start_date, year_month))
    results = cursor.fetchall()
    cursor.close()

    #Format the results
    formatted_results = []

    for result in results:
        month, genre, playbacks = result[0], result[1], result[2]

        formatted_result = {
            'month': f'month_{str(month)[-2:]}',
            'genre': genre,
            'playbacks': playbacks
        }

        formatted_results.append(formatted_result)

    #Prepare the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
        'results': formatted_results
    }
    return jsonify(response)

##########################################################
## LIST TOP10 SONGS

# GET http://localhost:8080/dbproj/top10
# {"token": token}

@app.route('/dbproj/top10', methods=['GET'])
def list_top10():

    #Verifications - - -

    if (check_result := check_request_body()) is not None: return check_result
    if (check_n_args := check_number_of_arguments(1)) is not None: return check_n_args
    if (check_args_result := check_required_arguments(['token'])) is not None: return check_args_result

    # Extract information from the request body - - -
    token = request.json.get('token')

    # Check values
    if (check_values_result := check_values([token])) is not None: return check_values_result

    #Verify token
    user_id = verify_token(token)
    if not isinstance(user_id, int): return user_id

    #Check if it's a consumer
    if (result := check_consumer(user_id)) is not None: return result

    #List top10 playlist
    cursor = db_connection().cursor()
    cursor.execute("""
        SELECT song_ismn, COUNT(*) AS play_count
        FROM logs
        WHERE consumer_person_id = %s AND initial_date >= (current_date - interval '30 days') -- Filter logs from the last 30 days
        GROUP BY song_ismn
        ORDER BY COUNT(*) DESC
        LIMIT 10;""", (user_id,))
    results = cursor.fetchall()
    cursor.close()

    #Format the results
    formatted_results = []

    for index, result in enumerate(results, start=1):
        number = str(index)
        song_id = result[0]
        n_plays = result[1]
        formatted_result = {
            'number': number,
            'song_id': song_id,
            'n_plays': n_plays
        }
        formatted_results.append(formatted_result)

    #Prepare the response
    response = {
        'status': StatusCodes['success'],
        'errors': None,
        'results': formatted_results
    }
    return jsonify(response)

##########################################################
## MAIN
##########################################################

if __name__ == '__main__':

    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080

    #Postman requests
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')