from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools import Tool, tool
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
from typing import Annotated
from langchain_community.chat_models import ChatAnthropic
from langchain_google_community.gmail.toolkit import GmailToolkit
from langchain_community.tools.gmail.utils import get_gmail_credentials, build_resource_service
from langchain_core.tools.structured import StructuredTool
import json
from typing import Optional, Dict, Any, List
import os
from datetime import datetime

load_dotenv(override = True)

class EmailInput(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: Optional[str] = Field(None, description="Email body; adapter will compose if missing")

class FileOutput(BaseModel):
    symbol : str = Field(..., description="The Stock Symbol")
    data : str = Field(..., description="The Output to be saved to the text file")

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



def send_mail_impl(
    to: str,
    subject: str,
    body: str,
    *,
    client_secrets_file: str = "credentials.json",
    token_path: str = "token.json",
    scopes: Optional[List[str]] = None,
    send_as_draft: bool = False,
) -> str:

    if scopes is None:
        scopes = ["https://mail.google.com/"]

    credentials = get_gmail_credentials(
        token_file="token.json",
        scopes=["https://mail.google.com/"],
        client_secrets_file="credentials.json",
    )
    api_resource = build_resource_service(credentials=credentials)

    toolkit = GmailToolkit(api_resource=api_resource)
    send_tool = next((t for t in toolkit.get_tools() if getattr(t, "name", None) == "GmailSendMessage"), None)
    draft_tool = [t for t in toolkit.get_tools() if t.name == "GmailCreateDraft"]

    payload = {"to": to, "subject": subject, "message": body}

    if send_as_draft:
        if draft_tool is None:
            raise RuntimeError("GmailCreateDraft tool not available.")
        result = draft_tool.run(payload)
        return f"Draft created. Result: {result}"
    else:
        if send_tool is None:
            raise RuntimeError("GmailSendMessage tool not available.")
        result = send_tool.run(payload)
        return f"Message Sent with Result: {result}"

def _safe_load_json_maybe(text: str) -> Any:
    """
    Try to parse JSON from a string that may contain JSON with newlines/escaped characters.
    Returns parsed object on success, otherwise returns None.
    """
    if not isinstance(text, str):
        return None
    text_strip = text.strip()
    try:
        return json.loads(text_strip)
    except Exception:
        try:
            return json.loads(text_strip.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"'))
        except Exception:
            start = text_strip.find("{")
            end = text_strip.rfind("}")
            if start != -1 and end != -1 and end > start:
                snippet = text_strip[start : end + 1]
                try:
                    return json.loads(snippet)
                except Exception:
                    return None
            return None


def flatten_body_field(body_field: Any) -> str:
    """
    Convert the `body` field into a plain text string suitable for an email body.
    Accepts:
      - a dict containing 'summary', 'sources', 'tools_used'
      - a JSON string encoding such a dict
      - a plain string
      - other values (stringified)
    """
    if isinstance(body_field, dict):
        summary = body_field.get("summary") or ""
        sources = body_field.get("sources") or []
        tools_used = body_field.get("tools_used") or []
        parts = []
        if summary:
            parts.append(summary.strip())
        if sources:
            parts.append("Sources: " + ", ".join(map(str, sources)))
        if tools_used:
            parts.append("Tools used: " + ", ".join(map(str, tools_used)))
        return "\n\n".join(parts).strip()

    if isinstance(body_field, str):
        parsed = _safe_load_json_maybe(body_field)
        if isinstance(parsed, dict):
            return flatten_body_field(parsed)
        return body_field.strip()

    return str(body_field)

def send_mail_adapter(*args, **kwargs) -> str:
    if kwargs:
        payload = dict(kwargs)
    elif args:
        first = args[0]
        if isinstance(first, str):
            parsed = _safe_load_json_maybe(first)
            if isinstance(parsed, dict):
                payload = parsed
            else:
                raise ValueError("Positional string tool input must contain JSON with to/subject (or use named args)")
        elif isinstance(first, dict):
            payload = first.copy()
        else:
            raise ValueError("Unsupported positional tool input type")
    else:
        payload = {}

    to = payload.get("to")
    subject = payload.get("subject")
    body_field = payload.get("body")

    body_text = flatten_body_field(body_field) if body_field is not None else ""

    if not body_text:
        llm = ChatAnthropic(model="claude-2.1", temperature=0)
        system = "You are a professional assistant. Write a concise, professional email body (3 short paragraphs max) summarizing the requested analysis."
        user = f"Subject: {subject}\n\nPlease produce the analysis summary to send in the email body."
        resp = llm.generate([{"role": "system", "content": system}, {"role": "user", "content": user}])
        try:
            body_text = resp.generations[0][0].text.strip()
        except Exception:
            body_text = f"Analysis for {subject or 'No Subject'} is not available."

    try:
        validated = EmailInput.model_validate({"to": to, "subject": subject, "body": body_text})
    except ValidationError as e:
        raise ValueError(f"Invalid email payload: {e}") from e

    return send_mail_impl(validated.to, validated.subject, validated.body)

send_mail_tool = StructuredTool.from_function(
    func=send_mail_adapter,
    name="send_mail_tool",
    description="Send an email",
    args_schema=EmailInput
)

def save_summary_to_file(symbol : str, data : str):
    """Saves the Stock Results Summary to a text file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{symbol}_research.txt"
    formatted_text = f"--- Stock Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
        f.write("\n\n")
    
    return f"Data for {symbol} successfully saved to {filename}"

save_to_file = StructuredTool.from_function(
    name = "save_to_file",
    func = save_summary_to_file,
    description = "Saves the Stock Results Summary to a text file",
    args_schema=FileOutput
)
