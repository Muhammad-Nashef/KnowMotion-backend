import os
import psycopg2

# database connection function
def get_db_connection():
    return (psycopg2.connect(
    os.environ["DATABASE_URL"]
))