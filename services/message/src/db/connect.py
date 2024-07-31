import boto3
import mysql.connector

from db.secrets import get_secrets

DB_NAME = "huskerlymessagingdb"

class DBConnection:
  def __init__(self):
    try:
      secrets = get_secrets()

      self.pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="huskerly-cp-message",
        pool_size=20,
        pool_reset_session=True,
        database=DB_NAME,
        host=secrets["db_ep"],
        user=secrets["user"],
        password=secrets["password"],
        ssl_disabled=False
      )
    except mysql.connector.Error as err:
      print(f"Failed to create MySQL connection pool. {err}")

  def __init__(self):
    self.client.close()

  def query(self, query_string, params=None):
    conn = self.pool.get_connection()
    cursor = conn.cursor()
    result = None
    
    try:
      cursor.execute(query_string, params)
      conn.commit()

      if cursor.rowcount and cursor.rowcount > 0:
        result = cursor.fetchall()
        
    except mysql.connector.Error as err:
      print(f"MySQL error: {err}")
      conn.rollback()

    # Close cursor and release the connection back to the pool
    cursor.close()
    conn.close()

    return result
      