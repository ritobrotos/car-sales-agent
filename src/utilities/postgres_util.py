import psycopg2
from psycopg2.extras import DictCursor


# Connect to the PostgreSQL database
def create_postgres_connection(my_db_name: str, my_db_user: str, my_db_password: str, my_db_host: str, my_db_port: str):
    return psycopg2.connect(
        dbname=my_db_name,
        user=my_db_user,
        password=my_db_password,
        host=my_db_host,
        port=my_db_port
    )


def execute_query(cursor: DictCursor, query: str):
    cursor.execute(query)
    return cursor.fetchall()


DB_NAME = "food_db"
DB_USER = "postgres"
DB_PASSWORD = "rito123"
DB_HOST = "localhost"
DB_PORT = "5432"


def test_execute_query():
    connection = create_postgres_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    select_query = "SELECT * FROM indian_food"
    cursor = connection.cursor(cursor_factory=DictCursor)
    rows = execute_query(cursor, select_query)

    for row in rows:
        print(row)


if __name__ == '__main__':
    test_execute_query()