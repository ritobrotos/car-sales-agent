from src.sales_agent.constants import GEMINI_API_KEY
from src.sales_agent.sales_agent_db_query_composer import validate_composed_sql_query
from src.sales_agent.sales_agent_db_query_executor import get_car_search_formatted_response_from_db
import google.generativeai as genai
from google.api_core import retry
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

test_drive_booking = []


def get_car_inventory_info(user_query: str) -> int:
    """Contains the car inventory as well as the car details like car make, model, car manufactured year, car color,
    mileage, transmission, and price."""
    sql_query = validate_composed_sql_query(user_query)
    db_response = get_car_search_formatted_response_from_db(sql_query)
    return db_response


def book_test_drive(user_query: str) -> str:
    """Book a test drive for the customer when following details are provided: car, name, email, phone_number,
    preferred_date, preferred_time."""
    class BookTestDrive(BaseModel):
        car: str = Field(description="")
        name: str = Field(description="Customer name")
        email: str = Field(description="Customer email address")
        phone_number: str = Field(description="Customer phone number")
        preferred_date: str = Field(description="Customer preferred date for test drive")
        preferred_time: str = Field(description="Customer preferred time for test drive")

    parser = PydanticOutputParser(pydantic_object=BookTestDrive)
    # Convert single quotes to double quotes
    user_query = user_query.replace("'", "\"")
    # Remove backslashes from the string
    user_query = user_query.replace("\\", "")
    try:
        test_drive_booking_info = parser.parse(user_query)
        test_drive_booking.append(test_drive_booking_info)
    except Exception as e:
        print("Error: ", e)
        return "Cannot book test drive: Invalid input or missing data."
    return "Test drive booked successfully."


def reserve_car(user_query: str) -> str:
    """Reserve a car for the user based on the user's query."""
    return "Car reserved successfully."


tools = [get_car_inventory_info, book_test_drive]

CAR_SALES_AGENT_PROMPT = """You are a Car sales assistant who is having a conversation with a human. \
    Your task is to assist the human in buying a car. You have access to tools which you can use to help customers \
    with their queries. 
    
    Your main objective is to book test drives for the customers. If a customer shows interest in a car, ask them if \
    they would like to book it for a test drive.
    
    If the customer likes a car then he/she can book a test drive for this car. For booking the car following details \
    are required, ask the customer all these information if he/she wants to book a test drive.
    
    car: car information
    name: customer name
    email: customer email
    phone_number: customer phone number
    preferred_date: customer preferred date for test drive
    preferred_time: customer preferred time for test drive
    
    Use the tool book_test_drive to book a test drive for the customer. This tool accepts information in json format.
    
    Here is an example of how to process test drive request:
    The user sends the below test drive booking details request: 
    I want to book a test drive for a Ford EcoSport. My name is John Doe and my phone number is 1234567890. john.doe@gmail.com is my email address. I would like to book the test drive on 3rd May at 11am.
    
    The user's test drive booking details request is converted into json format as below:
    {'car': 'Ford EcoSport', 'name': 'John Doe', 'email': 'john.doe@gmail.com', 'phone_number': '1234567890', 'preferred_date': '3rd May', 'preferred_time': '11am'}
    
    The json format string shown above should be passed to the tool book_test_drive to book the test drive for the customer. Make sure it is a valid json format string.
    """

genai.configure(api_key=GEMINI_API_KEY)


def get_gemini_1_5_pro_convo():
    model_name = 'gemini-1.5-pro-latest'
    model = genai.GenerativeModel(
        model_name, tools=tools, system_instruction=CAR_SALES_AGENT_PROMPT)
    convo = model.start_chat(enable_automatic_function_calling=True)
    return convo


def get_gemini_1_pro_convo():
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
  return convo.send_message(message)


def start_conversation():
    # While loop that runs as long as the test_drive_booking list is empty
    while not test_drive_booking:
        response = send_message(input('> '))
        print(response.text)


if __name__ == '__main__':
    start_conversation()