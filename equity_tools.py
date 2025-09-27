from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools import Tool

internet_search = DuckDuckGoSearchResults()
internet_search_tool = Tool(
    name="internet_search",
    func=internet_search.run,
    description="Search the web using DuckDuckGo for information",
)