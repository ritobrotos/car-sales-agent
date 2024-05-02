from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agent_init import create_sales_agent
from sales_agent_helper import get_llm


llm = get_llm()
memory = ConversationBufferMemory(memory_key="chat_history")
agent_executor = create_sales_agent()
chat_history = []


# Incomplete function, does not do the actual work
def get_sales_agent_response(user_message: str):
    template = """You are a Car sales chatbot who is having a conversation with a human. \
    Your task is to assist the human in buying used car.
    
    {human_input}
    """

    prompt = PromptTemplate(
        input_variables=["human_input"], template=template
    )

    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    response = chain.invoke({"human_input": user_message})
    print(response)

    return response


def get_sales_agent_response_from_agent(user_message: str):
    result = agent_executor.invoke({"input": user_message, "chat_history": chat_history})
    return result



# Define tools here



from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser


def test_agent():
    response = get_sales_agent_response_from_agent("I am looking for a second hand ford car with a sunroof and heated seats. Do you have any models in stock that fit that description?")
    print(response)


if __name__ == "__main__":
    test_agent()