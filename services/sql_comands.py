import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

class SQLMachine():
    def create_connection(self):
        connection = pymysql.connect(
            host=os.getenv('DATABASE_IP'),
            port=int(os.getenv('DATABASE_PORT')),
            user=os.getenv('DATABASE_UNAME'),
            passwd=os.getenv('DATABASE_PWORD'),
            autocommit=True
        )
        return connection

    def select(self, schema, table, ):
        connection = self.create_connection()

        with connection.cursor() as cursor:
            query = f"SELECT * FROM {schema}.{table}"
            cursor.execute(query)

            result = cursor.fetchall()
        
        connection.close()
        return result