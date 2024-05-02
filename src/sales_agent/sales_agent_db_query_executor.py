from src.utilities.postgres_util import create_postgres_connection, execute_query

from psycopg2.extras import DictCursor
import os
import sys

# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# # Add the parent directory to the Python path
# sys.path.insert(1, parent_dir + '/common_utilities')
# print("parent_dir: ", parent_dir)

DB_NAME = "car_db"
DB_USER = "postgres"
DB_PASSWORD = "rito123"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_car_search_formatted_response_from_db(sql_query: str):
    connection = create_postgres_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    cursor = connection.cursor(cursor_factory=DictCursor)
    sql_query = sql_query.strip('`').replace('sql', '')
    rows = execute_query(cursor, sql_query)

    if (len(rows) == 0):
        return "No cars found matching your search criteria."

    response = '';
    if (len(rows) > 3):
        response += f"We have {len(rows)} cars that matches your search criteria. Here are the top 3:\n"
    else:
        response += "Following are the cars that matches your search criteria:\n"

    for row in rows[:min(3, len(rows))]:
        # Example: Ford Ecosport Titanium build in 2018 with 50000 miles on it. This is a fully automatic car with a price of $15000. It is available in white color.
        car_info = f"{row['make']} {row['model']} built in {row['model_year']} with {row['mileage']} miles on it. This is a {row['transmission']} car with a price of ${row['price']}. It is available in {row['color']} color. "
        response += car_info + '\n'
    print("DB search response: ", response, "\n\n")
    return response


def test_get_car_search_formatted_response_from_db():
    query = "SELECT * FROM car where make = 'Honda'"
    response = get_car_search_formatted_response_from_db(query)
    print(response)


if __name__ == '__main__':
    test_get_car_search_formatted_response_from_db()