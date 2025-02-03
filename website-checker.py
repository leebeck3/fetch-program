import sys
import time
import socket
import logging
import concurrent.futures
import yaml
import urllib3
import multiprocessing
from urllib.parse import urlparse

class Logger:
    def __init__(self):
        self.logger = logging.getLogger('error_log')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('errors.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)

class Site: 
    def __init__(self, name: str, url: str, method: str, headers: dict, body: str):
            self.name = name
            self.url = url
            self.method = method
            self.headers = headers
            self.body = body
            self.domain = urlparse(url).netloc
            self.total_success = 0
            self.total_attempts = 0

class Monitor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.websites = self.load_websites()
        self.logger = Logger()
        self.max_threads = (multiprocessing.cpu_count() * 4)
        self.http = urllib3.PoolManager(maxsize=self.max_threads)

    def load_websites(self):
        websites = []
        with open(self.filepath, 'r') as file:
            data = yaml.safe_load(file)
        for entry in data:
            websites.append(Site(entry.get('name'), entry.get('url'), entry.get('method', "GET"), entry.get('headers', {}), entry.get('body', None)))
        return websites
            
    def check_website(self, site):
        try:
            response = self.http.urlopen(method=site.method,url=site.url,headers=site.headers,body=site.body,timeout=0.5,retries=False)
            site.total_attempts += 1
            if 200 <= response.status < 300:
                site.total_success += 1

        except Exception as e:
            self.logger.log_error(f"Error monitoring {site.url}: {e}")

    def monitor_websites(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.check_website, site): site for site in self.websites}
            self.print_stats()

    def print_stats(self):
        for site in self.websites:
            domain_stats = {}
            for site in self.websites:
                if site.domain not in domain_stats:
                    domain_stats[site.domain] = {'total_success': 0, 'total_attempts': 0}
                domain_stats[site.domain]['total_success'] += site.total_success
                domain_stats[site.domain]['total_attempts'] += site.total_attempts

            for domain, stats in domain_stats.items():
                if stats['total_attempts'] > 0:
                    uptime_percentage = round((stats['total_success'] / stats['total_attempts']) * 100)
                else:
                    uptime_percentage = 0
                print(f"{domain} has {uptime_percentage}% uptime availability")
            if site.total_attempts > 0:
                site.uptime_percentage = round((site.total_success / site.total_attempts) * 100)
            else:
                site.uptime_percentage = 0
            print(f"{site.domain} has {site.uptime_percentage}% uptime availability")

    def waste_time(self, future_time):
        time_to_wait = round(future_time - time.time(), 2)
        if time_to_wait < 0:
            sys.exit(f"The program is taking {round(time.time() - (timer - 15), 2)} seconds to run, perform performance engineering!.")
        print(f"\nWaiting {time_to_wait} seconds before the next check...")
        time.sleep(time_to_wait)
        future_time = time.time() + 15
        return future_time

if __name__ == "__main__":
    future_time = time.time() + 15
    if len(sys.argv) not in [2, 3]:
        print("Usage: python3 main.py /path/to/inputs.yaml")
        sys.exit(1)
    filepath = sys.argv[1]
    monitor = Monitor(filepath)
    while True:
        try:
            monitor.monitor_websites()
            future_time = monitor.waste_time(future_time)
        except KeyboardInterrupt:
            sys.exit()