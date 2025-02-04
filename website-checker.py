import sys
import time
import concurrent.futures
import yaml
import urllib3
import multiprocessing
from urllib.parse import urlparse

class Monitor:
    def __init__(self):
        self.websites = []
        self.results = {}
        self.max_threads = (multiprocessing.cpu_count() * 4)
        self.http = urllib3.PoolManager(maxsize=self.max_threads)
        self.future_time = time.time() + 15

    def load_websites(self, filepath):
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        for entry in data:
            if urlparse(entry.get('url')).netloc not in self.results:
                self.results[urlparse(entry.get('url')).netloc] = {'total_success': 0, 'total_attempts': 0}
        self.websites = data
            
    def check_website(self, website):
        self.results[urlparse(website.get('url')).netloc]['total_attempts'] += 1
        response = self.http.urlopen(method=website.get('method', "GET"),url=website.get('url'),headers=website.get('headers', {}),body=website.get('body', None),timeout=0.5,retries=False)
        if 200 <= response.status < 300:
            self.results[urlparse(website.get('url')).netloc]['total_success'] += 1

    def monitor_websites(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.check_website, website): website for website in self.websites}

    def print_stats(self):
        for domain in self.results:
            uptime_percentage = round((self.results[domain]['total_success'] / self.results[domain]['total_attempts']) * 100)
            print(f"{domain} has {uptime_percentage}% uptime availability")

    def sleep(self):
        time_to_wait = round(self.future_time - time.time(), 2)
        if time_to_wait < 0:
            sys.exit(f"The program is taking {round(time.time() - (self.future_time - 15), 2)} seconds to run, perform performance engineering!.")
        print(f"\nWaiting {time_to_wait} seconds before the next check...")
        time.sleep(time_to_wait)
        self.future_time = time.time() + 15

if __name__ == "__main__":
    monitor = Monitor()
    if len(sys.argv) != 2:
        print("Usage: python3(python) main.py /path/to/inputs.yaml")
        sys.exit(1)
    monitor.load_websites(sys.argv[1])
    while monitor.future_time >= time.time():
        monitor.monitor_websites()
        monitor.print_stats()
        monitor.sleep()