from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")


def check_for_car_db_call(user_message: str):
    examples = [
        {"input": "Hi! I'm looking for a reliable used car under $10,000.", "output": "yes"},
        {"input": "I'm in the market for a new SUV with a sunroof, heated seats, and advanced safety features. Do you have any models in stock that fit that description?", "output": "yes"},
        {"input": "I found the perfect car, but I'm curious about the financing options you offer. Can you tell me more about loan rates and down payment requirements?", "output": "no"},
    ]
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    # print(few_shot_prompt.format())

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Figure out if the message is an inquiry about a car with specific feature."),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )

    output_parser = StrOutputParser()
    chain = final_prompt | llm | output_parser
    return chain.invoke({"input": user_message})


# response = check_for_car_db_call("I am looking for a second hand ford car with a sunroof and heated seats. Do you have any models in stock that fit that description?")
# print(response)

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

class Car(BaseModel):
    make: str | None = Field(description="Car manufacturer (e.g., Toyota, Honda)")
    model: str | None = Field(description="Car model name (e.g., Camry, Accord)")
    model_year: str | None = Field(description="Year the car model was manufactured")
    color: str | None = Field(description="Color of the car")
    mileage: str | None = Field(description="Current mileage of the car")
    transmission: str | None = Field(description="Transmission type (Automatic or Manual)")
    price: str | None = Field(description="Asking or purchase price of the car")


def pydantic_approach():
    parser = PydanticOutputParser(pydantic_object=Car)

    prompt = PromptTemplate(
        template="Convert the user's query into the provided format.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    # print(chain.invoke({"query": "Honda city fully automatic, model should be after 2021 within the range of 15K"}))
    response = chain.invoke({"query": "I am looking for a second hand ford car with a sunroof and heated seats. Do you have any models in stock that fit that description?"})
    print(response)
    print(type(response))
    print(response.make) # ------> Thats the correct output