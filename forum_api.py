# Created by Kevin Zhu
# This file is the main file to run.
# create_table_example.sql provides an example case of what kind of table this API can work with.
# requirements.txt should be in the same folder as this file. It lists the dependencies to install for this application.
#
# Additional modules part of this API:
# users_table_SQL.py, which contains the SQL functions to work with the PostgreSQL database.
# db_config.json, which contains the sensitive configuration info to connect to the PostgreSQL database.
# mail_JWT_config.json, which contains the mail client and JWT configuration info.
# hash_code_functions.py, which contains the functions for storing the user password in a hash code.
# constants.py, which contains the constants including fields, which can be modified.
# These files should all be in the same folder.
# This app requires Python 3.7 or later.

from routes.user_routes import *
from routes.post_routes import *

if __name__ == '__main__':
    app.run()
