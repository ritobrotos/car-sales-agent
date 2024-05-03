from src.sales_agent.book_test_drive_composer import process_book_test_drive_request
from src.sales_agent.constants import GEMINI_API_KEY, CAR_SALES_AGENT_PROMPT
from src.sales_agent.sales_agent_db_query_composer import validate_composed_sql_query
from src.sales_agent.sales_agent_db_query_executor import get_car_search_formatted_response_from_db, \
    get_car_search_formatted_detailed_response_from_db
import google.generativeai as genai
from google.api_core import retry

test_drive_booking = []


def car_info(user_query: str):
    """Contains the car inventory info and few details of the car like car_id, make, model, car manufactured year,
    mileage, transmission, and price."""
    sql_query = validate_composed_sql_query(user_query)
    db_response = get_car_search_formatted_response_from_db(sql_query)
    return db_response


def detailed_car_info(user_query: str):
    """Contains detailed information of the car like car_id, make, model, car manufactured year, mileage, transmission,
    price, car color, fuel type, ownership, and car insurance validity date."""
    sql_query = validate_composed_sql_query(user_query)
    db_response = get_car_search_formatted_detailed_response_from_db(sql_query)
    return db_response


def book_test_drive(user_query: str) -> str:
    """Book a test drive for the customer when following details are provided: car, name, email, phone_number,
    preferred_date, preferred_time."""
    return process_book_test_drive_request(user_query)


def reserve_car(user_query: str) -> str:
    """Reserve a car for the user based on the user's query."""
    return "Car reserved successfully."


tools = [car_info, detailed_car_info, book_test_drive, reserve_car]

genai.configure(api_key=GEMINI_API_KEY)


def get_gemini_1_5_pro_convo():
    model_name = 'gemini-1.5-pro-latest'
    model = genai.GenerativeModel(
        model_name, tools=tools, system_instruction=CAR_SALES_AGENT_PROMPT)
    convo = model.start_chat(enable_automatic_function_calling=True)
    return convo


def get_gemini_1_pro_convo():
    print("Creating Gemini 1.0 Pro convo")
    model_name = 'gemini-1.0-pro-latest'
    model = genai.GenerativeModel(model_name, tools=tools)
    convo = model.start_chat(
        history=[
            {'role': 'user', 'parts': [CAR_SALES_AGENT_PROMPT]},
            {'role': 'model', 'parts': ['OK I understand. I will do my best!']}
        ],
        enable_automatic_function_calling=True)
    return convo


convo = get_gemini_1_pro_convo()


@retry.Retry(initial=30)
def send_message(message):
    gemini_agent_response = convo.send_message(message)
    # log_it(str(convo.history))
    response_text = gemini_agent_response.text.replace("$", r"\$")
    return response_text


def log_it(logs: str):
    with open('/Users/ritobrotoseth/Documents/workspace/python/car-sales-agent/src/sales_agent/logs/agent_history.log', 'a') as f:
        f.write(logs)
        f.write("================================\n\n")


def start_conversation():
    # While loop that runs as long as the test_drive_booking list is empty
    while not test_drive_booking:
        response = send_message(input('> '))
        print(response)


if __name__ == '__main__':
    start_conversation()