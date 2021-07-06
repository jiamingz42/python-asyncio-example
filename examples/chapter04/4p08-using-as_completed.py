import asyncio
import aiohttp
from aiohttp import ClientSession
from util import async_timed
from chapter_04 import fetch_status
 
 
@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [fetch_status(session, 'https://www.example.com', 1),
                    fetch_status(session, 'python://www.example.com', 1),
                    fetch_status(session, 'https://www.example.com', 5)]
 
        for finished_task in asyncio.as_completed(fetchers):
            try:
                print(await finished_task)
            except AssertionError:
                print("AssertionError")
 
 
asyncio.run(main())