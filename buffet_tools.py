from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools import Tool, tool
from dotenv import load_dotenv

load_dotenv()


internet_search = DuckDuckGoSearchResults()
internet_search_tool = Tool(
    name="internet_search",
    func=internet_search.run,
    description="Search the web using DuckDuckGo for information",
)

@tool
def income_statements(symbol:str) -> str:
    """Returns the annual and quarterly income statements for the company of interest."""
    import requests
    response = requests.get('https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol='+symbol+'&apikey={ALPHA_ADVANTAGE_API_KEY}')
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
    description="Returns the annual and quarterly income statements for the company of interest",
)

