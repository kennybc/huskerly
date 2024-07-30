from psycopg2 import pool
from utils.aws import get_aws_secret


def init_connection_pool(dbname):
    secret_name = "huskerly-db-credentials"
    credentials = get_aws_secret(secret_name)
    try:
        connection_pool = pool.SimpleConnectionPool(
            1,  # Minimum number of connections
            20,  # Maximum number of connections
            dbname=dbname,
            user=credentials['username'],
            password=credentials['password'],
            host=credentials['host'],
            sslmode='require',
        )
    except:
        print("Error initializing connection pool")
        return None
    return connection_pool


invites_connection_pool = None


def connect_to_invites_database():
    global invites_connection_pool

    if not invites_connection_pool:
        invites_connection_pool = init_connection_pool("invitesdb")
    conn = invites_connection_pool.getconn()
    return conn


def run_sql_file(file_path):
    conn = connect_to_invites_database()
    try:
        with conn.cursor() as cursor:
            with open(file_path, 'r') as file:
                sql = file.read()
                cursor.execute(sql)
                conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error executing SQL file: {e}")
    finally:
        invites_connection_pool.putconn(conn)
