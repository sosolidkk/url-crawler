from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup as bs
from requests.exceptions import (
    ConnectionError,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
)

BASE_URL = "https://scrapethissite.com/"
HOSTNAME = urlparse(BASE_URL).hostname

urls_queue = deque([BASE_URL])
processed_urls = set()
site_local_urls = set()
site_foreign_urls = set()
site_broken_urls = set()

while any(urls_queue):
    current_url = urls_queue.popleft()
    processed_urls.add(current_url)

    print(f"Current URL: {current_url}")
    print(f"Queue size {len(urls_queue)}")
    print(f"Queue: {urls_queue}")

    try:
        response = requests.get(current_url)
    except (ConnectionError, InvalidURL, InvalidSchema, MissingSchema):
        site_broken_urls.add(current_url)
        continue

    if "Content-Type" in response.headers:
        content_type = response.headers.get("Content-Type", None)
        if content_type is None or "text/html" not in content_type:
            continue

    soup = bs(response.text, "html.parser")
    anchor_tags = soup.find_all("a")

    for anchor in anchor_tags:
        # Find href attr
        attr = anchor.attrs.get("href") if "href" in anchor.attrs else None
        # Join relative URLs
        url = urljoin(BASE_URL, attr)

        # Check if url is local or foreign
        if HOSTNAME in url:
            site_local_urls.add(url)
        else:
            site_foreign_urls.add(url)

    print(f"Local urls [{len(site_local_urls)}]: {site_local_urls}")
    print(f"Foreign urls [{len(site_foreign_urls)}]: {site_foreign_urls}")

    for local_url in site_local_urls:
        if local_url not in urls_queue and local_url not in processed_urls:
            print("Appending queue: ", local_url)
            urls_queue.append(local_url)
