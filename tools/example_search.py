from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

search = DuckDuckGoSearchResults()

@tool
def web_search(query: str) -> str:
    """Search the web for current, real-time information (news, prices, recent events)."""
    return search.invoke(query)
