from datetime import timedelta

# Constants (can modify the first five):


# Name the fields/columns that you would like to store data for each user, by listing them in this tuple:
# DESIRED_FIELDS. There should be at least one element in this tuple. Note the email and password and already fields
# and do not need to be listed here. This tuple should match the database structure. As in create_table_example.sql,
# in this example, first_name and last_name are the desired fields that the database will store.
DESIRED_FIELDS = ('first_name', 'last_name')


# Specify the API URI.
# API_URI = 'http://localhost:5000'
API_URI = 'https://kevin.microfac.com'
# Specify the app URI (I used create-react-app).
# APP_URI = 'http://localhost:3000'
# APP_URI = 'http://localhost'

# APP_URI = 'http://kevinzhu.me'
APP_URI = 'https://kevin.microfac.com'

# APP_URI_LIST = ['https://localhost', 'https://localhost:3000']

# Choose the number of minutes before each access token expires with this constant.
MINUTES_BEFORE_TOKEN_EXPIRE = 30

# Choose the name of the server.
SERVER_NAME = "Kevin's Forum"

# Choose the length of the salt value for password hashing. 32 should be fine.
SALT_LENGTH = 32

# It is not necessary to modify anything below this line.
# ----------------------------------------------------------------------------------------------------------------------


TIME_TO_EXPIRE = timedelta(minutes=MINUTES_BEFORE_TOKEN_EXPIRE)

separator = ', '
COLUMNS_TO_SELECT = 'user_id, email, username, ' + separator.join(DESIRED_FIELDS)

COLUMNS_TO_INSERT = 'hash_code, email, username, ' + separator.join(DESIRED_FIELDS) + ', verified'

# Represents the fields to insert into for parameterized statements. Includes the desired fields as well as email and
# username. verified is always given FALSE. hash code is formatted differently because it is a byte array.
FIELDS_LENGTH = len(DESIRED_FIELDS) + 2

POSTS_INFO_TO_SELECT = "P.post_id, P.author_id, P.title, U.username, P.created_timestamp"

POSTS_KEYS = ('post_id', 'author_id', 'title', 'username', 'created_timestamp')

SINGLE_POST_INFO_TO_SELECT = "P.author_id, P.title, U.username, P.created_timestamp, P.content"

SINGLE_POST_KEYS = ('author_id', 'title', 'username', 'created_timestamp', 'content')

AUTHOR_POST_INFO_TO_SELECT = "post_id, title, created_timestamp"

AUTHOR_POST_KEYS = ('post_id', 'title', 'created_timestamp')