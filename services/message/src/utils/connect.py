import mysql.connector
from mysql.connector import pooling
from utils.error import ServerError, UserError
from utils.secrets import get_secrets
from contextlib import contextmanager
from botocore.exceptions import NoCredentialsError, ClientError, EndpointConnectionError

invites_connection_pool = None
secrets = get_secrets()


def initialize_db_connection():
    global invites_connection_pool
    invites_connection_pool = init_connection_pool("huskerlymessagingdb")


def init_connection_pool(dbname):
    try:
        return pooling.MySQLConnectionPool(
            pool_name="huskerly-message-db-pool",
            pool_size=8,  # Maximum number of connections
            pool_reset_session=True,
            database=dbname,
            user=secrets["db_user"],
            password=secrets["db_pass"],
            host=secrets["db_ep"],
            ssl_disabled=False,
            connection_timeout=10,
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


@contextmanager
def get_cursor():
    conn = connect_to_invites_database()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except (ClientError, NoCredentialsError, UserError, EndpointConnectionError) as e:
        conn.rollback()
        raise UserError(f"Client error: {str(e)}")
    except (ServerError) as e:
        conn.rollback()
        raise ServerError(f"Server error: {str(e)}")
    except Exception as e:
        conn.rollback()
        raise ServerError(f"An unexpected error occurred: {str(e)}")
    finally:
        cursor.close()
        conn.close()