from dotenv import load_dotenv
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from  langchain.agents.agent import AgentExecutor
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from equity_tools import internet_search_tool


load_dotenv()

class StockResponse(BaseModel):
    stock: str
    summary: str
    sources: list[str]
    tools_used: list[str]

#LLM 
anthropic_model = ChatAnthropic(model="claude-sonnet-4-20250514")

#Creating Parser from BaseModel
parser = PydanticOutputParser(pydantic_object=StockResponse)


#Equity Researcher Prompt 
anthropic_prompt = ChatPromptTemplate([
    ( 
        "system",
        """
        You are a stock researcher that will help choose a stock that will succeed.
        There are 10 parameters for success
            1. Debt/Equity is less than 0.5
            2. Current Ratio greater than 1.5 and less than 2.5
            3. Price/Book Ratio less than 1.5
            4. Return on Equity greater than 8 percent and increasing or remaining constant over the last 10 years
            5. Return on Assets greater than 6%
            6. Stable Book Value Growth
            7. Stable EPS Growth
            8. Stable Dividend Growth
            9. Wide Moat in its industry
            10. Interest coverage ratio greater than 5. 
        Answer the user query using the neccessary tools
        Wrap the output in this format and provide no other text\n{format_instructions}
        """,
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}"),
]).partial(format_instructions = parser.get_format_instructions())


anthropic_tools = [internet_search_tool]

#AI Agent
meet_agent0 = create_tool_calling_agent(anthropic_model, anthropic_tools, anthropic_prompt) 
agent_executor = AgentExecutor(agent = meet_agent0, tools = anthropic_tools, verbose = True)
query = input("What Stock Symbols would you like me to research?")
print(agent_executor.invoke({"query": query}))


'''
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
print(message.content)
'''