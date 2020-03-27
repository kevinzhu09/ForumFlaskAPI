from datetime import timedelta

# Constants (can modify the first five):


# Name the fields/columns that you would like to store data for each user, by listing them in this tuple:
# DESIRED_FIELDS. There should be at least one element in this tuple. Note the email and password and already fields
# and do not need to be listed here. This tuple should match the database structure. As in create_table_example.sql,
# in this example, first_name and last_name are the desired fields that the database will store.
DESIRED_FIELDS = ('first_name', 'last_name')

# Specify the API URI.
API_URI = 'http://localhost:5000'
# Specify the app URI (I used create-react-app).
APP_URI = 'http://localhost:3000'


# Choose the number of minutes before each access token expires with this constant.
MINUTES_BEFORE_TOKEN_EXPIRE = 20

# Choose the name of the server.
SERVER_NAME = "Kevin's Database"

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

POST_INFO_TO_SELECT = "P.post_id, U.username, P.title, P.created_timestamp"
