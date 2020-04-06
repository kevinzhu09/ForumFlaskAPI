from os import path
from json import load
from datetime import timedelta

dirname = path.dirname(__file__)
APIConfig_filename = path.join(dirname, 'config', 'APIConfig.json')

with open(APIConfig_filename) as file:
    APIConfig = load(file)
    mail_data = APIConfig["mail"]
    JWT_data = APIConfig["JWT"]
    db_data = APIConfig["database"]
    APP_URI = APIConfig["APP_URI"]
    SALT_LENGTH = APIConfig["SALT_LENGTH"]
    TIME_TO_EXPIRE = APIConfig["TOKEN_TTL_MINUTES"]
    TOKEN_TTL_MINUTES = timedelta(minutes=TIME_TO_EXPIRE)
    DESIRED_FIELDS = APIConfig["DESIRED_FIELDS"]
    SERVER_NAME = APIConfig["SERVER_NAME"]


separator = ', '
COLUMNS_TO_SELECT = 'user_id, email, username, ' + separator.join(DESIRED_FIELDS)

COLUMNS_TO_INSERT = 'hash_code, email, username, ' + separator.join(DESIRED_FIELDS) + ', verified'

FIELDS_LENGTH = len(DESIRED_FIELDS) + 2

POSTS_INFO_TO_SELECT = "P.post_id, P.author_id, P.title, U.username, P.created_timestamp"

POSTS_KEYS = ('post_id', 'author_id', 'title', 'username', 'created_timestamp')

SINGLE_POST_INFO_TO_SELECT = "P.author_id, P.title, U.username, P.created_timestamp, P.content"

SINGLE_POST_KEYS = ('author_id', 'title', 'username', 'created_timestamp', 'content')

AUTHOR_POST_INFO_TO_SELECT = "post_id, title, created_timestamp"

AUTHOR_POST_KEYS = ('post_id', 'title', 'created_timestamp')