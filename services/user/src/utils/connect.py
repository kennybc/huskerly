import mysql.connector
from mysql.connector import pooling
from utils.aws import get_aws_secret

invites_connection_pool = None


def init_connection_pool(dbname):
    secret_name = "huskerly-db-credentials"
    credentials = get_aws_secret(secret_name)
    try:
        return pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=16,  # Maximum number of connections
            pool_reset_session=True,
            database=dbname,
            user=credentials['username'],
            password=credentials['password'],
            host=credentials['host'],
            ssl_disabled=False,
            connection_timeout=10
        )
    except mysql.connector.Error as err:
        raise ValueError(f"Error initializing connection pool: {err}")


def connect_to_invites_database():
    global invites_connection_pool

    if not invites_connection_pool:
        invites_connection_pool = init_connection_pool("huskerlymessagingdb")

    if invites_connection_pool is None:
        raise ValueError("Failed to initialize connection pool")

    return invites_connection_pool.get_connection()
