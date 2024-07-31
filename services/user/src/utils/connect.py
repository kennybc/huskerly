import mysql.connector
from mysql.connector import pooling
from utils.aws import get_aws_secret
import logging


class DatabaseConnectionPool:
    _instance = None

    def __new__(cls, dbname):
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
            cls._instance._init_pool(dbname)
        return cls._instance

    def _init_pool(self, dbname):
        secret_name = "huskerly-db-credentials"
        credentials = get_aws_secret(secret_name)
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
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
            self.connection_pool = None
            raise ValueError(f"Error initializing connection pool: {err}")

    def get_connection(self):
        if self.connection_pool is None:
            raise ValueError("Connection pool is not initialized")
        return self.connection_pool.get_connection()

    def release_connection(self, conn):
        conn.close()


# Singleton instance for invites database
invites_db_pool = DatabaseConnectionPool("huskerlyinvitesdb")


def connect_to_invites_database():
    conn = None
    try:
        conn = invites_db_pool.get_connection()
        return conn
    except mysql.connector.Error as err:
        raise ValueError(f"Failed to get connection from pool: {err}")
    finally:
        if conn:
            invites_db_pool.release_connection(conn)
