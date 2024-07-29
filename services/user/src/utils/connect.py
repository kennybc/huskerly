from psycopg2 import pool
from utils.aws import get_aws_secret


def init_connection_pool(dbname):
    secret_name = "huskerly_credentials"
    credentials = get_aws_secret(secret_name)

    connection_pool = pool.SimpleConnectionPool(
        1,  # Minimum number of connections
        20,  # Maximum number of connections
        dbname=dbname,
        user=credentials['username'],
        password=credentials['password'],
        host=credentials['host'],
        sslmode='require',
    )
    return connection_pool


invites_connection_pool = init_connection_pool("huskerlyinvites")


def connect_to_invites_database():
    global invites_connection_pool

    if not invites_connection_pool:
        invites_connection_pool = init_connection_pool("huskerlyinvites")
    conn = invites_connection_pool.getconn()
    return conn
