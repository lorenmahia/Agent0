from dotenv import load_dotenv
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from  langchain.agents.agent import AgentExecutor
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from summary_tools import summary_tool

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

#Summary Reporter Prompt 
anthropic_prompt = ChatPromptTemplate([
    ( 
        "system",
        """
        You are a stock summary writer that analyzes text files and returns a summary of the most important traits of a good company
        based on value investing principles. YOu will return the exact verbage of the parameters the investors use to decide which is a 
        valuable company to invest in. Also include an formulas for custom ratios or values that the writer created by themselves.
        You will search the whole files and deliver the required information.
        Answer the user query using the neccessary tools
        Wrap the output in this format and provide no other text\n{format_instructions}
        """,
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}"),
]).partial(format_instructions = parser.get_format_instructions())

anthropic_tools = [summary_tool]

#AI Agent
summary_agent = create_tool_calling_agent(anthropic_model, anthropic_tools, anthropic_prompt) 
agent_executor = AgentExecutor(agent = summary_agent, tools = anthropic_tools, verbose = True)
query = input("What text file would you like me to summarize?")
print(agent_executor.invoke({"query": query}))