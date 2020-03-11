from datetime import timedelta

# Constants (can modify the first three):


# Name the fields/columns that you would like to store data for each user, by listing them in this tuple:
# DESIRED_FIELDS. There should be at least one element in this tuple. Note the email and password and already fields
# and do not need to be listed here.
DESIRED_FIELDS = ('first_name', 'last_name', 'phone_number')

# Specify the host URI.
HOST_URI = 'http://localhost:5000'


# Choose the number of minutes before each access token expires with this constant.
MINUTES_BEFORE_TOKEN_EXPIRE = 20

# Choose the length of the salt value for password hashing. 32 should be fine.
SALT_LENGTH = 32

# It is not necessary to modify anything below this line.
# ----------------------------------------------------------------------------------------------------------------------

FIELDS_LENGTH = len(DESIRED_FIELDS)

TIME_TO_EXPIRE = timedelta(minutes=MINUTES_BEFORE_TOKEN_EXPIRE)

separator = ', '
COLUMNS_TO_SELECT = 'user_id, email, ' + separator.join(DESIRED_FIELDS)

COLUMNS_TO_INSERT = separator.join(DESIRED_FIELDS) + ', hash_code, email'
