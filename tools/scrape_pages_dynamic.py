from typing import List
from langchain_core.tools import tool
from langchain_community.document_loaders import SeleniumURLLoader

def _truncate(text: str, max_length: int = 4000) -> str:
    """Truncate text to a maximum length."""
    if len(text) > max_length:
        return text[:max_length] + "... [truncated]"
    return text

@tool
def scrape_pages_dynamic(urls: List[str]) -> str:
    """Fetch and read JavaScript-rendered or anti-bot-protected webpages using
    a real headless browser (Selenium). Slower, so only use when scrape_pages
    fails or returns empty/garbled content (e.g. Substack and other SPA-style
    sites need this). Pass a list of exact URLs."""
    try:
        loader = SeleniumURLLoader(urls=urls, headless=True, continue_on_failure=True)
        docs = loader.load()
        if not docs:
            return f"Could not load any content from: {urls}"
        results = []
        for doc in docs:
            source = doc.metadata.get("source", "unknown URL")
            results.append(f"--- Content from {source} ---\n{_truncate(doc.page_content)}")
        return "\n\n".join(results)
    except Exception as e:
        return f"Error scraping {urls} with Selenium: {e}"
