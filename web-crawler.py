import asyncio
import aiohttp
import re

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from collections import deque
from typing import List, Set
from urllib.parse import urlparse


def extract_urls(url: str, html: str) -> Set[str]:
    o = urlparse(url)
    soup = BeautifulSoup(html, features="html.parser")
    links = set()
    for link in soup.findAll('a'):
        href = link.get('href') and link.get('href').strip()
        if href is None:
            continue
        if href.startswith('/'):
            links.add(f"{o.scheme}://{o.netloc}/{href.strip('/')}")
        elif href.startswith('http://') or href.startswith('https://'):
            links.add(href)
        elif href.startswith('#'):
            pass # safely ignore these
        else:
            print(f'[ERROR] Invalid URL {href}')

    return set(sorted(links)[:3])


async def get_next_urls(session: ClientSession, url: str) -> List[str]:
    async with session.get(url) as result:
        text = await result.text()
        return extract_urls(url, text)


async def main():
    seed_url = "https://pythonspot.com/extract-links-from-webpage-beautifulsoup/"
    seen = set([seed_url])

    async with aiohttp.ClientSession() as session:
        pending = {asyncio.create_task(get_next_urls(session, seed_url))}
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            next_urls = await next(iter(done))
            for next_url in next_urls:
                if next_url not in seen:
                    seen.add(next_url)
                    pending.add(asyncio.create_task(get_next_urls(session, next_url)))

    print(sorted(seen))

asyncio.run(main())
