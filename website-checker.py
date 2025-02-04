import sys
import time
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

class Site: 
    def __init__(self, name: str, url: str, method: str, headers: dict, body: str):
        self.name = name
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body
        self.domain = urlparse(url).netloc

class Monitor:
    def __init__(self):
        self.websites = []
        self.logger = Logger()
        self.results = {}
        self.max_threads = (multiprocessing.cpu_count() * 4)
        self.http = urllib3.PoolManager(maxsize=self.max_threads)
        self.future_time = time.time() + 15
        self.first_run = True

    def load_websites(self, filepath):
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        for entry in data:
            website = Site(entry.get('name'), entry.get('url'), entry.get('method', "GET"), entry.get('headers', {}), entry.get('body', None))
            self.websites.append(website)
            if website.domain not in self.results:
                self.results[website.domain] = {'total_success': 0, 'total_attempts': 0}
            
    def check_website(self, site):
        try:
            self.results[site.domain]['total_attempts'] += 1
            response = self.http.urlopen(method=site.method,url=site.url,headers=site.headers,body=site.body,timeout=0.5,retries=False)
            if 200 <= response.status < 300:
                self.results[site.domain]['total_success'] += 1
        except Exception as e:
            self.logger.log_error(f"Error monitoring {site.url}: {e}")

    def monitor_websites(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.check_website, site): site for site in self.websites}
            concurrent.futures.wait(futures)
            self.print_stats()

    def print_stats(self):
        for domain in self.results:
            if self.results[domain]['total_attempts'] > 0:
                uptime_percentage = round((self.results[domain]['total_success'] / self.results[domain]['total_attempts']) * 100)
            else:
                uptime_percentage = 0
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
        print("Usage: python3 main.py /path/to/inputs.yaml")
        sys.exit(1)
    monitor.load_websites(sys.argv[1])
    while monitor.future_time >= time.time():
        monitor.monitor_websites()
        monitor.sleep()