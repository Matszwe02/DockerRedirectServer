from flask import Flask, request, redirect
import os
import requests
import logging
import concurrent.futures
import re

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_urls_from_text(text_content):
    """Extracts URLs from plain text content using regex."""
    return re.findall(r'https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#]*)(?![\/])', text_content)

def is_url_reachable(url):
    logging.info(f'Checking {url}...')
    try:
        head_request = requests.head(url, timeout=5)
        success = head_request.status_code >= 200 and head_request.status_code < 400
        return success, url
    except:
        return False, url

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def redirect_to_target(path):
    target_urls = []
    urls_list_url = os.environ.get('URLS_LIST')

    if urls_list_url:
        try:
            # Prevent infinite loop if URLS_LIST points to itself
            if urls_list_url.startswith("http://localhost") or urls_list_url.startswith("http://127.0.0.1"):
                logging.warning("URLS_LIST points to the application itself. Skipping.")
            else:
                response = requests.get(urls_list_url, timeout=10)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                urls_from_text = extract_urls_from_text(response.text)
                target_urls.extend(urls_from_text)
                logging.info(f"Extracted URLs from URLS_LIST: {urls_from_text}")
        except requests.RequestException as e:
            logging.error(f"Error fetching or parsing URLS_LIST: {e}")

    target_urls_str = os.environ.get('TARGET_URLS')
    if target_urls_str:
        target_urls.extend([url.strip() for url in target_urls_str.split(',')])
    
    if not target_urls:
        return "No target URLs found", 503

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(is_url_reachable, url) for url in target_urls]
        for future in concurrent.futures.as_completed(futures):
            success, url = future.result()
            logging.info(f'{url}: {success}')
            if success:
                logging.info(f"Redirecting to: {url}")
                executor.shutdown(wait=False, cancel_futures=True)  # Stop other futures as soon as we have a success
                return redirect(url + "/" + path, code=301)

    logging.error(f"No working target URLs found from: {target_urls}")
    first_url = target_urls[0] if target_urls else None
    if first_url:
        return redirect(first_url + "/" + path, code=302)

    return "No working target URL found", 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
