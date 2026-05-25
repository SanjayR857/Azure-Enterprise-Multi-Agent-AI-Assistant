from langchain.tools import tool

from tavily import TavilyClient

from app.core.config import settings


client = TavilyClient(api_key=settings.TAVILY_API_KEY)


@tool
def web_search(query: str) -> str:
    """
    Search the web for real-time, current, up-to-date, or general knowledge information on any topic.
    Use this tool whenever the user asks about:
    - Recent events, current news, live facts, weather, or real-time data.
    - Factual verification of concepts, places, people, or details that are not in your training set.
    - Information requiring an external search query on the internet.
    - Complex inquiries where fetching multiple web search summaries provides a more accurate answer.
    
    Args:
        query (str): The search query or search keywords (e.g. 'current news on AI regulations').
        
    Returns:
        str: Summaries and links of search results.
    """

    try:

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )

        results = []

        for item in response["results"]:

            results.append(
                f"Title: {item['title']}\n"
                f"Content: {item['content']}\n"
                f"URL: {item['url']}\n"
            )

        return "\n\n".join(results)

    except Exception as e:
        return f"Search Error: {str(e)}"