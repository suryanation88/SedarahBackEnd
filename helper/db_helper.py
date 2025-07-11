"""DB Helper"""
import os
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import Error

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'db_donor')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password123')
DB_POOL_NAME = os.environ.get('DB_POOL_NAME', 'donor_pool')
POOL_SIZE = int(os.environ.get('POOL_SIZE', 10))

db_pool = MySQLConnectionPool(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    pool_size=POOL_SIZE,
    pool_name=DB_POOL_NAME
)

def get_connection():
    """
    Get connection db connection from db pool
    """
    connection = db_pool.get_connection()
    connection.autocommit = True
    return connection

def close_connection(connection):
    """
    Close database connection properly
    """
    try:
        if connection and connection.is_connected():
            connection.close()
    except Error as e:
        print(f"Error closing connection: {e}")
