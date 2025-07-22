import aiohttp
import os
from typing import List, Dict, Any
from fastapi import HTTPException
import logging

BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def brave_search(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    if not BRAVE_SEARCH_API_KEY:
        raise ValueError("Brave Search API key is not set")

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_SEARCH_API_KEY
    }
    params = {
        "q": query,
        "count": num_results
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BRAVE_SEARCH_URL, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("web", {}).get("results", [])
                else:
                    logger.error(f"Error in Brave Search: {response.status}")
                    raise HTTPException(status_code=response.status, detail="Error in Brave Search")
    except aiohttp.ClientError as e:
        logger.error(f"Network error during Brave Search: {str(e)}")
        raise HTTPException(status_code=500, detail="Network error during search")

async def search_missing_info(topic: str) -> str:
    try:
        results = await brave_search(f"educational content about {topic}")
        if results:
            return f"Here's some information about {topic}:\n\n" + "\n\n".join(
                f"- {result['title']}: {result['description']}" for result in results[:3]
            )
        else:
            logger.warning(f"No results found for topic: {topic}")
            return f"Sorry, I couldn't find any information about {topic}."
    except Exception as e:
        logger.error(f"Error searching for missing info: {str(e)}")
        return "An error occurred while searching for information. Please try again later."