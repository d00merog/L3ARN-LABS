import aiohttp
import os
from typing import List, Dict, Any

BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

async def brave_search(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_SEARCH_API_KEY
    }
    params = {
        "q": query,
        "count": num_results
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(BRAVE_SEARCH_URL, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("web", {}).get("results", [])
            else:
                print(f"Error in Brave Search: {response.status}")
                return []

async def search_missing_info(topic: str) -> str:
    results = await brave_search(f"educational content about {topic}")
    if results:
        return f"Here's some information about {topic}:\n\n" + "\n\n".join(
            f"- {result['title']}: {result['description']}" for result in results[:3]
        )
    else:
        return f"Sorry, I couldn't find any information about {topic}."