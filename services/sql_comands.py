import pymysql
from dotenv import load_dotenv
import os

# Use our .env file to set up the environment variables.
load_dotenv()

class SQLMachine():
    def create_connection(self):
        """
        Creates a connection to the SQL database specified by the
        environment variables.

        Returns the connection.
        """
        connection = pymysql.connect(
            host=os.getenv('DATABASE_IP'),
            port=int(os.getenv('DATABASE_PORT')),
            user=os.getenv('DATABASE_UNAME'),
            passwd=os.getenv('DATABASE_PWORD'),
            autocommit=True
        )
        return connection

    def select(self, schema, table, ):
        """
        Select everything from a certain table in a schema within
        the database.
        """
        # construct our query.
        query = f"SELECT * FROM {schema}.{table}"

        connection = self.create_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        
        connection.close()

        return result

    def insert(self, schema, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))

        query = f"INSERT INTO {schema}.{table} ({columns}) VALUES ({placeholders})"

        connection = self.create_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, tuple(data.values()))
        
        connection.close()

    def select_user_info(self, schema, table, user_id):
        """
        Select specific user information from the table in the database.
        """
        query = f"SELECT name, email, profile_pic FROM {schema}.{table} WHERE id = %s"

        connection = self.create_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result
        finally:
            connection.close()
        