from dotenv import load_dotenv
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from  langchain.agents.agent import AgentExecutor
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from buffet_tools import internet_search_tool, income_statements, balance_sheets, cash_flow, news_sentiment, send_mail_tool, save_to_file


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
        You will give the stock a percentage score representing the number of parameters it passed. 
        These are the parameters for success
            1. Debt/Equity < 0.5
            2. Current Ratio greater than 1.5 and less than 2.5
            3. Price/Book Ratio less than 1.5.  Focus on tangible book value adjusted for understated assets 
               (appreciated real estate, investment securities) and overstated assets (goodwill, obsolete inventory)
            4. Return on Equity greater than 8 percent and increasing or remaining constant over the last 10 years
            5. Return on Assets greater than 6%
            6. Stable Book Value Growth
            7. Stable EPS Growth
            8. Uninterrupted dividend payments for at least 20 years and consistent dividend policy indicating management discipline
            9.  Wide competitive moats through brand identity, monopoly position, economies of scale, or unique assets
            10. Interest coverage ratio greater than 5.
            11. Long-term debt not exceeding working capital for industrials
            12. For utilities: debt should not exceed 2x stock equity at book value
            13. Earnings stability with some earnings in each of the past 10 years.
            14. Minimum earnings growth of at least one-third over past 10 years (using 3-year averages)
            15. Coverage ratios for bonds: Industrial companies need 7x earnings coverage before taxes, utilities 4x, railroads 5x.
            16. Moderate P/E ratio: Current price no more than 15x average earnings of past 3 years
            17.  Price to book value no more than 1.5x
            18. P/E ratio times price-to-book ratio should not exceed 22.5
            19. Overall earnings/price ratio should be at least as high as current high-grade bond rate
            20. Adequate enterprise size ($100M+ annual sales for industrials, $50M+ assets for utilities)
            21. Sustainable growth (10% pretax or 6-7 percent after-tax long-term rates)
            22.  Strong management that acts in shareholder interests
            23. Companies that generate more cash than they consume
            24.  Net-current-asset value purchases at 2/3 or less of stripped-down asset value
            25. Stock/Equity ratio for bonds measuring market price of junior issues to total debt
            26. Two-part appraisal process: past-performance value based on historical data, then adjusted for future prospects
            27. High Valuation if it is a Growth Stock. Use this valuation formula: Value = Current Earnings times (8.5 + 2 times Expected Annual Growth Rate)
            28. Simple, understandable businesses with predictable cash flows; companies producing undifferentiated/homogeneous products
            29. Insiders who invest their own money alongside shareholders; management with stock options aligned with share price performance; 
                shareholder-oriented management taking value-realization actions
            30. Companies with catalysts for value realization (spinoffs, liquidations, share buybacks)

        Answer the user query using the neccessary tools
        Wrap the output in this format and provide no other text and save it to a text file in the current directory.\n{format_instructions}
        """,
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}"),
]).partial(format_instructions = parser.get_format_instructions())


anthropic_tools = [ income_statements, balance_sheets, cash_flow, news_sentiment, save_to_file]

#AI Agent
def call_buffet_agent(symbol: str):
    buffet_agent = create_tool_calling_agent(anthropic_model, anthropic_tools, anthropic_prompt) 
    agent_executor = AgentExecutor(agent = buffet_agent, tools = anthropic_tools, 
                                    agent_type="structured-chat-zero-shot-react-description", verbose = True)
    print(agent_executor.invoke({"query": symbol}))