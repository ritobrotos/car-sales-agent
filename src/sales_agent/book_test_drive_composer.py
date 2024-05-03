from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

from src.sales_agent.sales_agent_helper import get_llm
import json

llm = get_llm()


def process_book_test_drive_request(user_query: str) -> str:
    natural_language_to_json_prompt = """
    You are a natural language processor, you take human language and transform it into a valid JSON object. \
    For the provided natural language string input you need to convert it into a JSON object. \
    Following are the attribute / field description of the JSON object:
    
    car - The car information for which the test drive is to be booked.
    name - Customer name
    email - Customer email address
    phone_number - Customer phone number
    preferred_date - Customer preferred date for test drive
    preferred_time - Customer preferred time for test drive
    
    Below is the natural language which you need to convert into a JSON object:
    """
    system_prompt_template = SystemMessagePromptTemplate.from_template(natural_language_to_json_prompt)

    final_prompt_template = ChatPromptTemplate.from_messages(
        [
            system_prompt_template,
            ("human", "{input}"),
        ]
    )

    output_parser = StrOutputParser()
    chain = final_prompt_template | llm | output_parser
    composed_json_object = chain.invoke({"input": user_query})
    composed_json_object = clean_generated_json(composed_json_object)

    # Retry can fix the issue
    while is_valid_json(composed_json_object) == False:
        composed_json_object = chain.invoke({"input": user_query})
        composed_json_object = composed_json_object.strip('`').replace("json", "")
        # Convert single quotes to double quotes
        composed_json_object = composed_json_object.replace("'", "\"")
        # Remove backslashes from the string
        composed_json_object = composed_json_object.replace("\\", "")

    return parse_json_to_book_test_drive_object(composed_json_object)


def clean_generated_json(composed_json_object: str) -> str:
    composed_json_object = composed_json_object.strip('`').replace("json", "")
    # Convert single quotes to double quotes
    composed_json_object = composed_json_object.replace("'", "\"")
    # Remove backslashes from the string
    composed_json_object = composed_json_object.replace("\\", "")
    return composed_json_object

def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False


def parse_json_to_book_test_drive_object(json_data: str) -> str:
    class BookTestDrive(BaseModel):
        car: str = Field(description="The car_id of the car for which the test drive is to be booked.")
        name: str = Field(description="Customer name")
        email: str = Field(description="Customer email address")
        phone_number: str = Field(description="Customer phone number")
        preferred_date: str = Field(description="Customer preferred date for test drive")
        preferred_time: str = Field(description="Customer preferred time for test drive")
    parser = PydanticOutputParser(pydantic_object=BookTestDrive)
    try:
        test_drive_booking_info = parser.parse(json_data)
        # test_drive_booking.append(test_drive_booking_info)
    except Exception as e:
        print("Error: ", e)
        return "Cannot book test drive: Invalid input or missing data."
    print("Book test drive json: ", json_data)
    return "Test drive booked successfully."