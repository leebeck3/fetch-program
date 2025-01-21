import sys
import time
import logging
import concurrent.futures
from urllib.parse import urlparse
#third party libraries
import yaml
import urllib3
import docstring

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
error_log = logging.getLogger('error_log')
error_log.setLevel(logging.ERROR)
error_handler = logging.FileHandler('errors.log')
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
error_log.addHandler(error_handler)
error_log.propagate = False

def import_variables():
    if len(sys.argv) > 3:
        print("Usage: python3 main.py /path/to/inputs.yaml <maxworkers>")
        sys.exit(1)
    filepath = sys.argv[1]
    if len(sys.argv) == 3:
        maxworkers = int(sys.argv[2])
    else:
        #five seems to be a good default variables across all my test devices
        maxworkers = 5
    return filepath, maxworkers

def import_file(filepath):
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        sys.exit(f"File not found: {file_path}")
    except yaml.YAMLError as e:
        sys.exit(f"Error parsing YAML file: {e}")
    except Exception as e:
        sys.exit(f"Unexpected error: {e}")

def validate_input(data):
    """
    Validate and standardize input data.
    Required fields: name, url
    Optional fields: method (default: GET), headers (default: {}), body (default: None)
    Logs errors to 'errors.log' for invalid entries.
    Returns a list of valid website entries.
    """
    validated_list = []
    for entry in data:
        try:
            name = entry.get('name')
            url = entry.get('url')
            if not name or not url:
                raise ValueError(f"Missing 'name' or 'url' in entry: {entry}")
                return None

            if entry.get('body') is not None:
                headers = "application/json"
            else:
                headers = {}

            validated_list.append({
                'name': name,
                'url': url,
                'method': entry.get('method', 'GET'),
                'headers': entry.get('headers', headers),
                'body': entry.get('body', None)
            })
        except Exception as e:
            error_log.error(f"Validation error for entry {entry}: {e}")
    return validated_list


def monitor_website_async(websites, maxworkers):
    """
    Monitor websites asynchronously.
    Returns a list of results with True/False in the 'success' field:
    - True if connection time <= 500ms and response status is 200 <= status < 300.
    - False otherwise.
    """
    results = []
    http = urllib3.PoolManager(maxsize=maxworkers)

    def get_domain(url):
        """Extract the domain name from a URL."""
        return urlparse(url).netloc

    def check_site(site):
        try:
            start_time = time.time()
            response = http.request(
                method=site['method'],
                url=site['url'],
                headers=site['headers'],
                body=site['body'],
                timeout=None,
                retries=False
            )
            elapsed_time_ms = (time.time() - start_time) * 1000
            success = elapsed_time_ms <= 500 and 200 <= response.status < 300
            return {
                'name': site['name'],
                'domain': get_domain(site['url']),
                'status': response.status,
                'latency': elapsed_time_ms,
                'success': success
            }
        except Exception as e:
            error_log.error(f"Error monitoring {site['url']}: {e}")
            return {
                'name': site['name'],
                'domain': get_domain(site['url']),
                'status': 'Error',
                'latency': None,
                'success': False
            }

    with concurrent.futures.ThreadPoolExecutor(max_workers=maxworkers) as executor:
        futures = [executor.submit(check_site, site) for site in websites]
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                site = futures[future]
                error_log.error(f"Error in ThreadPoolExecutor for {site['url']}: {e}")
                results.append({
                    'name': site['name'],
                    'domain': get_domain(site['url']),
                    'status': 'Error',
                    'latency': None,
                    'success': False
                })

    return results

def print_stats(results, domain_uptime):
    """Print website uptime statistics in the specified format."""


    for result in results:
        domain = result['domain']
        if domain not in domain_uptime:
            domain_uptime[domain] = {'success_count': 0, 'total_count': 0}
        domain_uptime[domain]['total_count'] += 1
        if result['success']:
            domain_uptime[domain]['success_count'] += 1

    for domain, counts in domain_uptime.items():
        uptime_percentage = round((counts['success_count'] / counts['total_count']) * 100)
        print(f"{domain} has {uptime_percentage:.1f}% uptime availability")

def waste_time(timer):
    '''
    Waste time to ensure the program runs in batches every 15 seconds
    It's probably possible to overflow this, seems highly unlikely though.
    '''
    time_to_wait = round(timer - time.time(), 2)
    if time_to_wait < 0:
        sys.exit(f"The program is taking {round(time.time() - (timer - 15), 2)} seconds to run, perform performance engineering!.")
    print(f"\nWaiting {time_to_wait} seconds before the next check...")
    time.sleep(time_to_wait)
    timer = time.time() + 15
    return timer

if __name__ == "__main__":
    #keep timer at start to ensure accurate timing within the program's context
    timer = time.time() + 15
    domain_uptime = {}
    filepath, maxworkers = import_variables()
    data = import_file(filepath)
    validated_data = validate_input(data)

    print(f"Scanning {len(data)} websites every 15 seconds...")
    try:
        while True:
            #make synchronous and lump in 
            monitoring_results = monitor_website_async(validated_data, maxworkers)
            print_stats(monitoring_results, domain_uptime)
            timer = waste_time(timer)
    except KeyboardInterrupt:
        sys.exit()
