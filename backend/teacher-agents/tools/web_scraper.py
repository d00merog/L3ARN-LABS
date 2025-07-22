import aiohttp
from bs4 import BeautifulSoup

async def scrape_webpage(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                # Extract and return relevant content
                # This is a basic implementation and may need to be adjusted based on specific requirements
                return soup.get_text()
            else:
                return f"Error: Unable to fetch the webpage. Status code: {response.status}"
