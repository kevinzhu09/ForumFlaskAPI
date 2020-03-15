1.Create the table in the database. It should include 
hash code as type:bytea, email, and some other string 
variables. These other string variables should match the
DESIRED_FIELDS tuple in constants.py.

See create_table_example.sql to demonstrate this.
(I tested with PostgreSQL)

2.Update db_config.json with the database configuration
info. 

3.Update mail_JWT_config.json with your mail server info.
4.Update constants.py if desired.
5.Install the dependencies from requirements.txt.

6. Run and use the API.