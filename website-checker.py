import yaml
import requests
import sys
import time
import traceback
import signal
from urllib.parse import urlparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

VALID_HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
error_log = logging.getLogger('error_log')
error_log.setLevel(logging.ERROR)
error_handler = logging.FileHandler('errors.log')
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
error_log.addHandler(error_handler)

def get_domain_name(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

class Website:
    def __init__(self, website_data, verbosity=False):
        self.name = website_data.get('name')
        self.url = website_data.get('url')
        self.method = website_data.get('method', 'GET').upper()
        self.headers = website_data.get('headers', {})
        self.body = website_data.get('body', None)
        self.verbosity = verbosity
        if not self.name or not self.url:
            raise ValueError(f"Missing 'name' or 'url' for website entry: {website_data}")
        if self.method not in VALID_HTTP_METHODS:
            raise ValueError(f"Unsupported HTTP method '{self.method}' for URL: {self.url}")

    @property
    def requests_method(self):
        try:
            method_func = getattr(requests, self.method.lower())
            response = method_func(self.url, headers=self.headers, data=self.body, timeout=0.5)
            return response
        except requests.RequestException as e:
            if self.verbosity:
                error_log.error(f"Error accessing {self.url} ({self.method}): {e}")
            return None

    def check_status(self):
        response = self.requests_method
        return response and 200 <= response.status_code < 300

def calculate_uptime(up_count, total_count):
    return 100 * (up_count / total_count) if total_count > 0 else 0

def monitor_website(website_data, stats, verbosity):
    try:
        website = Website(website_data, verbosity)
        is_up = website.check_status()
        domain = get_domain_name(website.url)
        key = (domain, website.method)
        stats[key]["total_count"] += 1
        if is_up:
            stats[key]["up_count"] += 1
    except ValueError as e:
        if verbosity:
            error_log.error(f"{e}")
        return

def handle_keyboard_interrupt(verbosity):
    """Handle keyboard interrupt to print tracebacks if verbosity is enabled."""
    if verbosity:
        traceback.print_exc()
    sys.exit(0)

if __name__ == "__main__":
    verbosity = False

    
    if len(sys.argv) < 2:
        print("Usage: python3 main.py /path/to/inputs.yaml [--verbosity]")
        sys.exit(1)

    # Check for the --verbosity argument
    if '--verbosity' in sys.argv:
        verbosity = True

    file_path = sys.argv[1]

    # Handle KeyboardInterrupt, cleans up user input a bit.
    signal.signal(signal.SIGINT, lambda sig, frame: handle_keyboard_interrupt(verbosity))

    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        if not isinstance(data, list):
            print("The YAML file must contain a list of websites.")
            sys.exit(1)

        stats = defaultdict(lambda: {"up_count": 0, "total_count": 0})
        print("Starting endpoint monitoring every 15 seconds... (Press Ctrl+C to stop)")
        print("------------------------------------------------")

        with ThreadPoolExecutor() as executor:
            while True:
                futures = []
                for website_data in data:
                    futures.append(executor.submit(monitor_website, website_data, stats, verbosity))

                for future in as_completed(futures):
                    future.result()

                domain_uptime = defaultdict(lambda: {"up_count": 0, "total_count": 0})
                for (domain, method), counts in stats.items():
                    domain_uptime[domain]["total_count"] += counts["total_count"]
                    domain_uptime[domain]["up_count"] += counts["up_count"]

                for domain, counts in domain_uptime.items():
                    uptime_percentage = calculate_uptime(counts["up_count"], counts["total_count"])
                    print(f"{domain} has {uptime_percentage:.1f}% uptime")
                print("------------------------------------------------")

                # Countdown timer
                for i in range(15, 0, -1):
                    print(f"Next check in {i} seconds... (Ctrl+C to stop)", end='\r')
                    time.sleep(1)

                print()  # To move to the next line after the countdown

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
