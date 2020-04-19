from os import environ
from json import load
from datetime import timedelta

# dirname = path.dirname(__file__)
# APIConfig_filename = path.join(dirname, 'APIConfig.json')
APIConfig_filename = environ.get('API_CONFIG_FILENAME')
print(APIConfig_filename)
with open(APIConfig_filename) as file:
    APIConfig = load(file)
    mail_data = APIConfig["mail"]
    JWT_data = APIConfig["JWT"]
    db_data = APIConfig["database"]
    google_data = APIConfig["google"]
    APP_URI = APIConfig["APP_URI"]
    SALT_LENGTH = APIConfig["SALT_LENGTH"]
    TOKEN_TTL_MINUTES = APIConfig["TOKEN_TTL_MINUTES"]
    TOKEN_TTL_TIMEDELTA = timedelta(minutes=TOKEN_TTL_MINUTES)
    SERVER_NAME = APIConfig["SERVER_NAME"]
    SERVER_EMAIL = APIConfig["SERVER_EMAIL"]
