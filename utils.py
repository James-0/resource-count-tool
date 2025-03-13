import aiohttp
import asyncio
from config import JIRA_BASE_URL, HEADERS

async def fetch_page(session, url):
    """Fetch a single page from the Jira API"""
    async with session.get(url, headers=HEADERS) as response:
        response.raise_for_status()
        return await response.json()

async def fetch_paginated_data(endpoint, max_results=100):
    """Fetch paginated data asynchronously from Jira API"""
    all_data = []
    start_at = 0

    async with aiohttp.ClientSession() as session:
        while True:
            url = f"{JIRA_BASE_URL}{endpoint}?startAt={start_at}&maxResults={max_results}"
            data = await fetch_page(session, url)

            all_data.extend(data.get("values", data))  # Some APIs use 'values'

            if len(data) < max_results:
                break  # No more pages

            start_at += max_results

    return all_data
