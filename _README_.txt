Created by Kevin Zhu
forum_api_app is the main file to run.
SQL_scripts set up the database and tables.
requirements.txt should be in the same folder as this file. It lists the dependencies to install for this application.
Additional modules part of this API:
The "routes" folder contains the Flask app routes for the API.
The "routes/data_access" folder contains the SQL code for the API to contact the database.
hash_code_functions.py, which contains the functions for storing the user password in a hash code.
APIConfig.json, which contains the constants including fields, which can be modified.

This app requires Python 3.7 or later.

External modules: flask handles the URI routes for the API requests. It also allows JSON to be easily written.
flask_jwt_extended handles the JSON Web Tokens (JWT) integration which is used for login verification.
flask_mail handles the mail server.
json helps for reading .json files.