from flask import Flask, request, redirect
import os
import requests
import logging
import concurrent.futures
import re
import time

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
last_url = [None, 0]


def extract_urls_from_text(text_content) -> list[str]:
    """Extracts URLs from plain text content using regex."""
    return re.findall(r'https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#]*)(?![\/])', text_content)
    

def get_urls_list(request_url: str):
    try:
        urls = []
        response = requests.get(request_url, timeout=10)
        
        for item in extract_urls_from_text(response.text):
            if item.startswith("http://localhost") or item.startswith("http://127.0.0.1"):
                logging.warning("URLS_LIST points to the application itself. Skipping.")
            else:
                urls.append(item)
        logging.info(f"Extracted URLs from URLS_LIST: {urls}")
        return urls
    except Exception as e:
        logging.error(f"Error fetching or parsing URLS_LIST: {e}")
    return []


def is_url_reachable(url: str):
    url = url.strip().removesuffix('/')
    logging.info(f'Checking {url}...')
    try:
        head_request = requests.head(url, timeout=5)
        success = head_request.status_code >= 200 and head_request.status_code < 400
        return success, url
    except:
        return False, url


def try_redirect(urls: list[str]):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(is_url_reachable, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            success, url = future.result()
            logging.info(f'Requested {url}: {success}')
            if success:
                logging.info(f"Redirecting to: {url}")
                executor.shutdown(wait=False, cancel_futures=True)  # Stop other futures as soon as we have a success
                return url
    return None


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def redirect_to_target(path):
    global last_url
    
    if time.time() - last_url[1] < 600:
        logging.info(f'Using cached URL: {last_url[0]}')
        if is_url_reachable(last_url[0]):
            return redirect(last_url[0] + "/" + path, code=301)
        last_url = [None, 0]
    
    if target_urls_str := os.environ.get('TARGET_URLS'):
        if ret := try_redirect(target_urls_str.split(',')):
            last_url = [ret, time.time()]
            return redirect(ret + "/" + path, code=301)
    
    if urls_list_url := os.environ.get('URLS_LIST'):
        if ret := try_redirect(get_urls_list(urls_list_url)):
            last_url = [ret, time.time()]
            return redirect(ret + "/" + path, code=301)
    
    logging.error(f"No working target URLs found. Check logs.")
    return "No working target URL found", 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
