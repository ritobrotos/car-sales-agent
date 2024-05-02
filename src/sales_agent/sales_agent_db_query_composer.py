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
  vin VARCHAR(17) UNIQUE,                 -- Unique Vehicle Identification Number
  price DECIMAL(10,2) DEFAULT NULL,        -- Asking or purchase price of the car
  ownership VARCHAR(20) NOT NULL,            -- Ownership status (First, Second or Third Owner)
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
        "input": "I am looking for a ford ecosports with mileage less than 20k",
        "output": "SELECT * FROM car WHERE make = 'Ford' AND model = 'EcoSport' AND mileage < 20000"
    },
    {
        "input": "I am looking for a ford ecosports with mileage less than 20k and after 2019",
        "output": "SELECT * FROM car WHERE make = 'Ford' AND model = 'EcoSport' AND mileage < 20000 AND model_year > 2019"
    },
    {
        "input": "Honda city fully automatic, model should be after 2021 within the range of 15K",
        "output": "SELECT * FROM car WHERE make = 'Honda' AND model = 'City' AND transmission = 'Automatic' AND model_year > 2021 AND price < 15000"
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
    }
]

natural_language_to_sql_query_prompt = """You are a query translator, you take human natural language as input and convert it into a \
    valid Postgres SQL query.
    
    **Important:** When building the query, consider only the following columns from the `car` table: car_id, make, model, model_year, color, mileage, transmission, vin, price. Ignore any filters based on columns that are not present in the table (e.g., sunroof, heated_seats).
    
    Prepare the query using the information provided in the user's message. If a specific filter (e.g., transmission) is not mentioned by the user, omit that condition from the query.
    
    Below is the `car` table schema:
    {car_table_schema}
    
    Below are few examples of user messages and their corresponding SQL queries. Use these examples to convert the user message into a valid SQL query.
"""

validate_composed_sql_query_prompt = """You are an SQL query validator. You take a SQL query as input and validate the \
    SQL with the given table schema.
    If the SQL query is valid, return the query. If the SQL query is invalid, rectify the query and return.
    
    In case of scenarios where the input is not a SQL query then return NA as response.
    
    Below is the `car` table schema:
    {car_table_schema}
    
    Below are few examples of rectified SQL queries:
"""


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
    print("************************** Final Prompt from prepare_with_few_shot_prompt_sql_query: ",
          final_prompt_template.format_prompt(input=user_message, car_table_schema=car_table_schema).to_messages(), "\n")
    output_parser = StrOutputParser()
    chain = final_prompt_template | llm | output_parser
    composed_sql_query = chain.invoke({"input": user_message, "car_table_schema": car_table_schema})
    print("Composed SQL Query: ", composed_sql_query)
    print("**************************\n\n\n")
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
    print("************************** Final Prompt from validate_composed_sql_query: ",
          final_prompt_template.format_prompt(car_table_schema=car_table_schema, input=composed_sql_query).to_messages(),
          "\n")

    output_parser = StrOutputParser()
    chain = final_prompt_template | llm | output_parser
    rectified_query = chain.invoke({"car_table_schema": car_table_schema, "input": composed_sql_query})
    print("Rectified SQL Query: ", rectified_query)
    print("**************************\n\n\n")
    return rectified_query


if __name__ == '__main__':
    # user_query = "I am looking for a second hand ford car with a sunroof and heated seats. Do you have any models in stock that fit that description?"
    user_query = "Do you have any Honda cars in stock?"
    validate_composed_sql_query(user_query)