import mysql.connector
from mysql.connector import pooling
from utils.aws import get_aws_secret


def init_connection_pool(dbname):
    secret_name = "huskerly-db-credentials"
    credentials = get_aws_secret(secret_name)
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=20,  # Maximum number of connections
            pool_reset_session=True,
            database=dbname,
            user=credentials['username'],
            password=credentials['password'],
            host=credentials['host'],
            ssl_disabled=False,
        )
    except mysql.connector.Error as err:
        print(f"Error initializing connection pool: {err}")
        return None
    return connection_pool


invites_connection_pool = None


def connect_to_invites_database():
    global invites_connection_pool

    if not invites_connection_pool:
        invites_connection_pool = init_connection_pool("invitesdb")
    conn = invites_connection_pool.get_connection()
    return conn
