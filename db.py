# Description: This file contains the code to connect to the database.
import pyodbc
import os
from dotenv import load_dotenv

# Get the path of the .env file
env_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '', '')) + '\\.env'
print(env_path)

# Load the environment variables
load_dotenv(env_path)

pyodbc.pooling = False

# Begining of the function
server = str(os.getenv("server"))
db = str(os.getenv("db"))
user = str(os.getenv("user"))
pwd = str(os.getenv("pwd"))

# Define the connection string
connection_string = str('DRIVER={ODBC Driver 18 for SQL Server}; SERVER=' + server + 
                    '; DATABASE=' + db + 
                    '; UID=' + user + 
                    '; PWD=' + pwd + 
                    '; TrustServerCertificate=yes; MARS_Connection=yes;')

# Open connection to db
global conn
conn = pyodbc.connect(connection_string)

conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
#conn.setencoding(encoding='utf-8')