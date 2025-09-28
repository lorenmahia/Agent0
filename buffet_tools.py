from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools import Tool, tool
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
from typing import Annotated
from langchain_google_community.gmail.toolkit import GmailToolkit
from langchain_community.tools.gmail.utils import get_gmail_credentials, build_resource_service
from langchain_core.tools.structured import StructuredTool
import json
from typing import Any
import os

load_dotenv(override = True)

class EmailInput(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body")

internet_search = DuckDuckGoSearchResults()
internet_search_tool = Tool(
    name="internet_search",
    func=internet_search.run,
    description="Search the web using DuckDuckGo for information",
)

@tool
def income_statements(symbol:str) -> str:
    """Returns the annual income statements for the company of interest."""
    import requests
    response = requests.get('https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol='+symbol+'&apikey=' + os.getenv("ALPHA_ADVANTAGE_API_KEY"))
    symbol_overview = response.json()
    income_statements = dict()
    for year in range(len(symbol_overview['annualReports'])):
        income_statements[symbol_overview['annualReports'][year]['fiscalDateEnding']] = (
            f"""The annualReports for fiscalDateEnding {symbol_overview['annualReports'][year]['fiscalDateEnding']}, 
            reported in {symbol_overview['annualReports'][year]['reportedCurrency']},
            show a totalRevenue of {symbol_overview['annualReports'][year]['totalRevenue']} with a grossProfit of {symbol_overview['annualReports'][year]['grossProfit']}.
            The company incurred a costOfRevenue and costofGoodsAndServicesSold of {symbol_overview['annualReports'][year]['costOfRevenue']}.
            OperatingIncome stood at {symbol_overview['annualReports'][year]['operatingIncome']} with operatingExpenses of {symbol_overview['annualReports'][year]['operatingExpenses']},
            including sellingGeneralAndAdministrative expenses of {symbol_overview['annualReports'][year]['sellingGeneralAndAdministrative']} and
            researchAndDevelopment costs of {symbol_overview['annualReports'][year]['researchAndDevelopment']}. 
            DepreciationAndAmortization was recorded at {symbol_overview['annualReports'][year]['depreciationAndAmortization']}. 
            The company reported an incomeBeforeTax of {symbol_overview['annualReports'][year]['incomeBeforeTax']} and an incomeTaxExpense of {symbol_overview['annualReports'][year]['incomeTaxExpense']}. 
            NetIncome from continuing operations reached {symbol_overview['annualReports'][year]['netIncomeFromContinuingOperations']}, with a final 
            netIncome of {symbol_overview['annualReports'][year]['netIncome']}. The EBIT was {symbol_overview['annualReports'][year]['ebit']} and EBITDA was {symbol_overview['annualReports'][year]['ebitda']}, 
            reflecting strong profitability despite netInterestIncome at {symbol_overview['annualReports'][year]['netInterestIncome']} and 
            interestExpense of {symbol_overview['annualReports'][year]['interestExpense']}."""
        )

    return str(income_statements)

income_statements = Tool(
    name = "income_statements",
    func = income_statements,
    description="Returns the annual income statements for the company of interest",
)

@tool
def balance_sheets(symbol:str) -> str:
    """Returns the annual balance sheets for the company of interest"""
    import requests
    response = requests.get('https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol='+symbol+'&apikey=' + os.getenv("ALPHA_ADVANTAGE_API_KEY"))
    symbol_overview = response.json()
    balance_sheets = dict()
    for year in range(len(symbol_overview['annualReports'])):
        balance_sheets[symbol_overview['annualReports'][year]['fiscalDateEnding']] = (
            f"For the fiscal year ending {symbol_overview['annualReports'][year]['fiscalDateEnding']}, "
            f"reported in {symbol_overview['annualReports'][year]['reportedCurrency']}, the company reported total assets of "
            f"{symbol_overview['annualReports'][year]['totalAssets']}, including current assets of "
            f"{symbol_overview['annualReports'][year]['totalCurrentAssets']}. Cash and cash equivalents at carrying value were "
            f"{symbol_overview['annualReports'][year]['cashAndCashEquivalentsAtCarryingValue']}, with short-term investments of "
            f"{symbol_overview['annualReports'][year]['shortTermInvestments']} and inventory valued at "
            f"{symbol_overview['annualReports'][year]['inventory']}. Current net receivables amounted to "
            f"{symbol_overview['annualReports'][year]['currentNetReceivables']}, while non-current assets totaled "
            f"{symbol_overview['annualReports'][year]['totalNonCurrentAssets']}, including property, plant, and equipment at "
            f"{symbol_overview['annualReports'][year]['propertyPlantEquipment']}. Intangible assets, excluding goodwill, were "
            f"{symbol_overview['annualReports'][year]['intangibleAssetsExcludingGoodwill']}, with goodwill valued at "
            f"{symbol_overview['annualReports'][year]['goodwill']}. Total liabilities reached "
            f"{symbol_overview['annualReports'][year]['totalLiabilities']}, of which current liabilities accounted for "
            f"{symbol_overview['annualReports'][year]['totalCurrentLiabilities']}, including short-term debt of "
            f"{symbol_overview['annualReports'][year]['shortTermDebt']}. Non-current liabilities stood at "
            f"{symbol_overview['annualReports'][year]['totalNonCurrentLiabilities']}, featuring long-term debt of "
            f"{symbol_overview['annualReports'][year]['longTermDebt']}. Total shareholder equity was "
            f"{symbol_overview['annualReports'][year]['totalShareholderEquity']}, supported by retained earnings of "
            f"{symbol_overview['annualReports'][year]['retainedEarnings']}, common stock valued at "
            f"{symbol_overview['annualReports'][year]['commonStock']}, with "
            f"{symbol_overview['annualReports'][year]['commonStockSharesOutstanding']} shares outstanding."
        )
    
    return str(balance_sheets)

balance_sheets = Tool(
    name = "balance_sheets",
    func = balance_sheets,
    description = "Returns the annual balance sheets for the company of interest"
)

@tool
def cash_flow(symbol:str) -> str:
    """Returns the annual cash flow statements for the company of interest"""
    import requests
    response = requests.get('https://www.alphavantage.co/query?function=CASH_FLOW&symbol='+symbol+'&apikey=' + os.getenv("ALPHA_ADVANTAGE_API_KEY"))
    symbol_overview = response.json()
    cash_flow = dict()
    for year in range(len(symbol_overview['annualReports'])):
        cash_flow[symbol_overview['annualReports'][year]['fiscalDateEnding']] = (
        f"For the fiscal year ending {symbol_overview['annualReports'][year]['fiscalDateEnding']}, "
        f"reported in {symbol_overview['annualReports'][year]['reportedCurrency']}, the company generated an operating cash flow of "
        f"{symbol_overview['annualReports'][year]['operatingCashflow']}. Depreciation, depletion, and amortization expenses were "
        f"{symbol_overview['annualReports'][year]['depreciationDepletionAndAmortization']}, with capital expenditures totaling "
        f"{symbol_overview['annualReports'][year]['capitalExpenditures']}. Inventory changed by "
        f"{symbol_overview['annualReports'][year]['changeInInventory']}, while cash flow from investments was "
        f"{symbol_overview['annualReports'][year]['cashflowFromInvestment']} and cash flow from financing activities was "
        f"{symbol_overview['annualReports'][year]['cashflowFromFinancing']}. Dividend payouts amounted to "
        f"{symbol_overview['annualReports'][year]['dividendPayout']}, specifically for common stock at "
        f"{symbol_overview['annualReports'][year]['dividendPayoutCommonStock']}. The company recorded proceeds from repurchase of equity of "
        f"{symbol_overview['annualReports'][year]['proceedsFromRepurchaseOfEquity']}. Finally, net income for the year reached "
        f"{symbol_overview['annualReports'][year]['netIncome']}."
    )

    return str(cash_flow)

cash_flow = Tool(
    name = "cash_flow",
    func = cash_flow,
    description = "Returns the annual cash flow statements for the company of interest"
)

@tool
def news_sentiment(symbol:str) ->str:
    """Returns live and historical market news & sentiment data from a large & growing selection of premier news outlets for the selected stock symbol"""
    import requests
    response = requests.get('https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers='+symbol+'&apikey=' + os.getenv("ALPHA_ADVANTAGE_API_KEY"))
    symbol_overview = response.json()

    return str(symbol_overview)

news_sentiment = Tool(
    name = "news_sentiment",
    func = news_sentiment,
    description = "Returns live and historical market news & sentiment data from a large & growing selection of premier news outlets for the selected stock symbol"
)

@tool
def send_mail_impl(to: str, subject: str, body: str) -> str:
    """Send an email using Gmail via LangChain GmailToolkit."""
    credentials = get_gmail_credentials(
        token_path="token.json",
        scopes=["https://mail.google.com/"]
    )
    api_resource = build_resource_service(credentials=credentials)

    toolkit = GmailToolkit(api_resource=api_resource)
    send_tool = [t for t in toolkit.get_tools() if t.name == "GmailSendMessage"][0]

    result = send_tool.run({
        "to": to,
        "subject": subject,
        "message": body
    })

    return f"Sent to={to!r} subject={subject!r} body_len={len(body)}"

send_mail_tool = StructuredTool.from_function(
    func=send_mail_impl,
    name="send_mail_tool",
    description="Send an email",
    args_schema=EmailInput
)

