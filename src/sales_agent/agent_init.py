from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain.agents import tool
from langchain_core.prompts import MessagesPlaceholder
from sales_agent_db_query_composer import validate_composed_sql_query
from sales_agent_db_query_executor import get_car_search_formatted_response_from_db
from sales_agent_helper import get_llm
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents import AgentExecutor


llm = get_llm()


@tool
def get_car_inventory_info(user_query: str) -> int:
    """Contains the car inventory. Use this tool for searching any car related information specific too car make,
    car model, car manufactured year, car color, car mileage, car transmission, and car price."""
    sql_query = validate_composed_sql_query(user_query)
    db_response = get_car_search_formatted_response_from_db(sql_query)
    return db_response


def create_sales_agent():
    """
    Ref: https://python.langchain.com/docs/modules/agents/how_to/custom_agent/
    """
    MEMORY_KEY = "chat_history"
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Car sales assistant who is having a conversation with a human. \
                Your task is to assist the human in buying a car."""
            ),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    tools = [get_car_inventory_info]
    llm_with_tools = llm.bind_tools(tools)

    agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
                "chat_history": lambda x: x["chat_history"],
            }
            | prompt
            | llm_with_tools
        # | OpenAIToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor