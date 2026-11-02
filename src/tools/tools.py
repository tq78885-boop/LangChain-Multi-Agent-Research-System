from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """
    Perform a web search using the Tavily API.

    Args:
        query (str): The search query.

    Returns:
        str: The search results.
    """
    results = tavily.search(query=query,max_results=5)

    out = []
    for r in results['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:30]}\n")
    return "\n---------\n".join(out)

@tool
def scrape_url(url: str) -> str:
    """
    Fetch a webpage and extract its main text content.

    Args:
        url (str): The webpage URL to scrape.

    Returns:
        str: The page title, URL and extracted main content.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        return f"Failed to fetch {url}: {e}"

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""

    # 优先用 trafilatura 提取正文
    content = trafilatura.extract(html, include_comments=False, include_tables=True)

    # 回退方案 1：readability + BeautifulSoup
    if not content:
        try:
            doc = Document(html)
            title = title or doc.short_title()
            content = BeautifulSoup(doc.summary(), "html.parser").get_text("\n", strip=True)
        except Exception:
            content = ""

    # 回退方案 2：整页去标签取纯文本
    if not content:
        for tag in soup(["script", "style", "noscript", "iframe", "form"]):
            tag.decompose()
        content = soup.get_text("\n", strip=True)

    content = re.sub(r"\n{3,}", "\n\n", content).strip()
    if len(content) > 8000:
        content = content[:8000] + "\n...[truncated]"

    return f"Title: {title}\nURL: {url}\nContent:\n{content}"
