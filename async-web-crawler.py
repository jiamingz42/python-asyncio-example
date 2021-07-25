import asyncio
import functools
import time

from typing import List, Dict, Callable, Any
from collections import defaultdict, deque

FakeUrlMap: Dict[str, List[str]] = defaultdict(list)
FakeUrlMap["a"] = ["a", "b", "c"]
FakeUrlMap["b"] = ["c", "d"]
FakeUrlMap["c"] = ["b", "e", "f"]
FakeUrlMap["f"] = ["a", "g", "h"]

def async_timed():
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(f'starting {func} with args {args} {kwargs}')
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f'finished {func} in {total:.4f} second(s)')

        return wrapped

    return wrapper


@async_timed()
async def get_next_urls(curr_url, delay=0.5):
    await asyncio.sleep(delay)  # Fake a network IO
    return FakeUrlMap[curr_url]


@async_timed()
async def main():
    MAX_PENDING = 3

    seed_url = "a"

    visited = {seed_url}  # visited stores urls that have been added to queue
    queue = deque([seed_url])

    pending = set()

    while True:
        # Make sure there are at most 
        while len(queue) > 0 and len(pending) < MAX_PENDING:
            next_url = queue.popleft()
            pending.add(asyncio.create_task(get_next_urls(next_url)))
        
        if len(pending) == 0:
            break

        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for done_task in done:
            next_urls = await done_task
            for next_url in next_urls:
                if next_url not in visited:
                    queue.append(next_url)
                    visited.add(next_url)
        

    print(sorted(visited))


asyncio.run(main())
