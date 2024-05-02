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


def test_execute_query():
    db_name = "car_db"
    db_user = "postgres"
    db_password = "rito123"
    db_host = "localhost"
    db_port = "5432"

    connection = create_postgres_connection(db_name, db_user, db_password, db_host, db_port)
    select_query = "SELECT * FROM car"
    cursor = connection.cursor(cursor_factory=DictCursor)
    rows = execute_query(cursor, select_query)

    for row in rows:
        print(row)


if __name__ == '__main__':
    test_execute_query()