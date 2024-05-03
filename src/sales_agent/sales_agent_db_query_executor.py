from src.utilities.postgres_util import create_postgres_connection, execute_query

from psycopg2.extras import DictCursor

# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# # Add the parent directory to the Python path
# sys.path.insert(1, parent_dir + '/common_utilities')
# print("parent_dir: ", parent_dir)

DB_NAME = "car_db"
DB_USER = "postgres"
DB_PASSWORD = "rito123"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_search_response_from_db(sql_query: str):
    try:
        connection = create_postgres_connection(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
        cursor = connection.cursor(cursor_factory=DictCursor)
        sql_query = sql_query.strip('`').replace('sql', '')
        return execute_query(cursor, sql_query)
    except Exception as e:
        print("An error occurred when executing query: ", sql_query)


def get_car_search_formatted_response_from_db(sql_query: str):
    rows = get_search_response_from_db(sql_query)

    if rows is None:
        return "An error occurred, retry again with the specific query."

    if len(rows) == 0:
        return "No cars found matching your search criteria."

    if is_select_all_query(sql_query):
        response = '';
        if len(rows) > 3:
            response += f"We have {len(rows)} cars that matches your search criteria. Here are the top 3:\n"
        else:
            response += "Following are the cars that matches your search criteria:\n"
        for row in rows[:min(3, len(rows))]:
            # Example: Ford Ecosport Titanium build in 2018 with 50000 miles on it. This is a fully automatic car with a price of $15000. It is available in white color.
            car_info = car_info_string(row)
            response += car_info + '\n'
        print("DB search response: ", response)
        return response
    else:
        print("DB search response: ", str(rows))
        return str(rows)


def get_car_search_formatted_detailed_response_from_db(sql_query: str):
    rows = get_search_response_from_db(sql_query)

    if rows is None:
        return "An error occurred, retry again with the specific query."

    if len(rows) == 0:
        return "No cars found matching your search criteria."

    if is_select_all_query(sql_query):
        response = '';
        if len(rows) > 3:
            response += f"We have {len(rows)} cars that matches your search criteria. Here are the top 3:\n"
        else:
            response += "Following are the cars that matches your search criteria:\n"
        for row in rows[:min(3, len(rows))]:
            car_info = detailed_car_info_string(row)
            response += car_info + '\n'
        print("DB search response: ", response)
        return response
    else:
        print("DB search response: ", str(rows))
        return str(rows)


def detailed_car_info_string(row):
    detailed_car_info = f"car_id {row['car_id']}: {row['make']} {row['model']} built in {row['model_year']} with {row['mileage']} miles on it." \
               + f"This is a {row['transmission']} car with a price of {row['price']} USD. It is available in {row['color']} color." \
               + f"It is a {row['fuel_type']} car currently with {row['ownership']}. The insurance of the car is valid till {row['insurance_valid_date']}."
    return detailed_car_info


def car_info_string(row):
    car_info = f"car_id {row['car_id']}: {row['make']} {row['model']} built in {row['model_year']} with {row['mileage']} miles on it." \
        + f"This is a {row['transmission']} car with a price of {row['price']} USD."
    return car_info


def is_select_all_query(sql_query):
    # Convert the query to lowercase to make the search case-insensitive
    sql_query_lower = sql_query.lower()

    # Check if the query selects all columns
    if '*' in sql_query_lower.split('select', 1)[1].strip().split(' ', 1)[0]:
        return True
    else:
        return False


def test_get_car_search_formatted_response_from_db():
    query = "SELECT * FROM car where make = 'Honda'"
    response = get_car_search_formatted_response_from_db(query)
    print(response)


if __name__ == '__main__':
    test_get_car_search_formatted_response_from_db()