import sys
import time
import asyncio
import yaml
import aiohttp
from urllib.parse import urlparse

class AsyncMonitor:
    def __init__(self):
        self.websites = []
        self.results = {}
        self.future_time = time.time() + 15

    async def load_websites(self, filepath):
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        for entry in data:
            netloc = urlparse(entry.get('url')).netloc
            if netloc not in self.results:
                self.results[netloc] = {'total_success': 0, 'total_attempts': 0}
        self.websites = data

    async def check_website(self, session, website):
        netloc = urlparse(website.get('url')).netloc
        self.results[netloc]['total_attempts'] += 1
        try:
            async with session.request(
                method=website.get('method', "GET"),
                url=website.get('url'),
                headers=website.get('headers', {}),
                data=website.get('body', None),
                timeout=0.5
            ) as response:
                if 200 <= response.status < 300:
                    self.results[netloc]['total_success'] += 1
        except Exception:
            pass  # Handle connection errors gracefully

    async def monitor_websites(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_website(session, website) for website in self.websites]
            await asyncio.gather(*tasks)

    def print_stats(self):
        for domain, stats in self.results.items():
            if stats['total_attempts'] > 0:
                uptime_percentage = round((stats['total_success'] / stats['total_attempts']) * 100)
                print(f"{domain} has {uptime_percentage}% uptime availability")

    async def sleep(self):
        time_to_wait = round(self.future_time - time.time(), 2)
        if time_to_wait < 0:
            sys.exit(f"The program is taking {round(time.time() - (self.future_time - 15), 2)} seconds to run, perform performance engineering!")
        print(f"\nWaiting {time_to_wait} seconds before the next check...")
        await asyncio.sleep(time_to_wait)
        self.future_time = time.time() + 15

    async def run(self):
        while self.future_time >= time.time():
            await self.monitor_websites()
            self.print_stats()
            await self.sleep()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py /path/to/inputs.yaml")
        sys.exit(1)

    monitor = AsyncMonitor()
    asyncio.run(monitor.load_websites(sys.argv[1]))
    asyncio.run(monitor.run())