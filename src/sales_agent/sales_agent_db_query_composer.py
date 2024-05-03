from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from sales_agent_helper import get_llm

llm = get_llm()

car_table_schema = """CREATE TABLE car (
  car_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique identifier for the car (auto-increment)
  make VARCHAR(50) NOT NULL,             -- Car manufacturer (e.g., Toyota, Honda)
  model VARCHAR(100) NOT NULL,            -- Car model name (e.g., Camry, Accord)
  model_year INT NOT NULL,                 -- Year the car model was manufactured
  color VARCHAR(50) NOT NULL,             -- Color of the car
  mileage INT,                             -- Current mileage of the car
  transmission ENUM('Automatic', 'Manual'), -- Transmission type (Automatic or Manual)
  vin VARCHAR(17) UNIQUE,                    -- Unique Vehicle Identification Number
  price INT DEFAULT NULL,                   -- Asking or purchase price of the car
  ownership VARCHAR(20) NOT NULL,            -- Ownership status or the owner number (First Owner, Second Owner or Third Owner)
  fuel_type VARCHAR(20) NOT NULL,            -- Fuel type (Petrol, Diesel, Electric or CNG)
  insurance_valid_date DATE NOT NULL,       -- Insurance expiry date
);"""

few_shot_human_ai_example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

few_shot_nl_to_query_examples = [
    {
        "input": "Looking for car.",
        "output": "SELECT * FROM car"
    },
    {
        "input": "I am looking for a ford ecosports with mileage less than 80k",
        "output": "SELECT * FROM car WHERE make = 'Ford' AND model = 'EcoSport' AND mileage < 80000"
    },
    {
        "input": "I am looking for a ford ecosports with mileage less than 90k and after 2019",
        "output": "SELECT * FROM car WHERE make = 'Ford' AND model = 'EcoSport' AND mileage < 90000 AND model_year > 2019"
    },
]

few_shot_rectified_query_examples = [
    {
        "input": "SELECT * FROM car WHERE make = 'Ford' AND car_type = 'Used'",
        "output": "SELECT * FROM car WHERE make = 'Ford'"
    },
    {
        "input": """
            ```sql
            SELECT DISTINCT color
            FROM car
            WHERE make = 'Honda' AND model = 'Civic' AND model_year = 2023;
            ```
        """,
        "output": """
            SELECT DISTINCT color
            FROM car
            WHERE make = 'Honda' AND model = 'Civic' AND model_year = 2023;
        """
    },
    {
        "input": "Is there anything else I can help you with?",
        "output": "NA"
    }
]

natural_language_to_sql_query_prompt = """You are a query translator, you take human natural language as input and convert it into a \
    valid Postgres SQL query.
    
    **Important:** When building the query, consider only the below columns from the `car` table: 
    car_id, make, model, model_year, color, mileage, transmission, vin, price, ownership, fuel_type and insurance_valid_date. \
    Ignore any filters based on columns that are not present in the table (e.g., sunroof, heated_seats).
    
    Prepare the query using the information provided in the user's message. If a specific filter (e.g., transmission) is not mentioned by the user, omit that condition from the query.
    
    Below is the `car` table schema:
    {car_table_schema}
    
    Below are few examples of user message and their corresponding SQL queries.
"""

validate_composed_sql_query_prompt = """You are an SQL query validator. You take a SQL query as input and validate the \
    SQL with the given table schema.
    If the SQL query is valid, return the query. If the SQL query is invalid, rectify the query and return.
    
    In case of scenarios where the input text cannot be rectified to a valid query, return "NA" as response.
    
    Below is the `car` table schema:
    {car_table_schema}
    
    Below are few examples of rectified SQL queries:
"""


def log_it(logs: str):
    with open('/Users/ritobrotoseth/Documents/workspace/python/car-sales-agent/src/sales_agent/logs/query_composer.log', 'a') as f:
        f.write(logs)
        f.write("================================\n\n")


def prepare_with_few_shot_prompt_sql_query(user_message: str):
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=few_shot_human_ai_example_prompt,
        examples=few_shot_nl_to_query_examples,
    )

    system_prompt_template = SystemMessagePromptTemplate.from_template(natural_language_to_sql_query_prompt)

    final_prompt_template = ChatPromptTemplate.from_messages(
        [
            system_prompt_template,
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )

    # Final prompt send to the LLM
    # log_it("************************** Final Prompt from prepare_with_few_shot_prompt_sql_query: " \
    #     + str(final_prompt_template.format_prompt(input=user_message, car_table_schema=car_table_schema).to_messages()) \
    #     + "\n\n")

    output_parser = StrOutputParser()
    chain = final_prompt_template | llm | output_parser
    composed_sql_query = chain.invoke({"input": user_message, "car_table_schema": car_table_schema})
    print("Composed SQL Query: ", composed_sql_query)
    return composed_sql_query


def test_few_shot_prompt_sql_query():
    response = prepare_with_few_shot_prompt_sql_query("I am looking for a second hand ford car with a sunroof and heated seats. Do you have any models in stock that fit that description?")
    print(response)


def validate_composed_sql_query(user_query: str):
    composed_sql_query = prepare_with_few_shot_prompt_sql_query(user_query)
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=few_shot_human_ai_example_prompt,
        examples=few_shot_rectified_query_examples,
    )

    system_prompt_template = HumanMessagePromptTemplate.from_template(validate_composed_sql_query_prompt)
    final_prompt_template = ChatPromptTemplate.from_messages(
        [
            system_prompt_template,
            few_shot_prompt,
            ("human", "{input}"),
        ])

    # log_it("************************** Final Prompt from validate_composed_sql_query: " \
    #       + str(final_prompt_template.format_prompt(car_table_schema=car_table_schema, input=composed_sql_query).to_messages()) \
    #       + "\n")

    output_parser = StrOutputParser()
    chain = final_prompt_template | llm | output_parser
    rectified_query = chain.invoke({"car_table_schema": car_table_schema, "input": composed_sql_query})
    print("Verified SQL Query: ", rectified_query)
    return rectified_query


if __name__ == '__main__':
    # user_query_sample = "I am looking for a second hand ford car with a sunroof and heated seats. Do you have any models in stock that fit that description?"
    user_query_sample = "Do you have any Honda cars in stock?"
    validate_composed_sql_query(user_query_sample)