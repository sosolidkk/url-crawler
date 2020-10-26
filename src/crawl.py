import json
from collections import deque
from os import mkdir, path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup as bs
from requests.exceptions import ConnectionError, InvalidSchema, InvalidURL, MissingSchema


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def save_snap(current_url, soup):
    current_url = current_url.replace("https://", "")
    current_url = current_url.replace("/", "-")

    with open(f"snaps/{current_url}.html", "w") as file_writer:
        file_writer.write(soup.prettify())


def save_report(report):
    with open("report.json", "w") as json_file:
        json.dump(report, fp=json_file, sort_keys=True, indent=4)


def generate_report(processed_urls, local_urls, foreign_urls, broken_urls):
    report = {}

    report["processed_urls"] = {
        "qty": len(processed_urls),
        "urls": set_default(processed_urls),
    }
    report["local_urls"] = {
        "qty": len(local_urls),
        "urls": set_default(local_urls),
    }
    report["foreign_urls"] = {
        "qty": len(foreign_urls),
        "urls": set_default(foreign_urls),
    }
    report["broken_urls"] = {
        "qty": len(broken_urls),
        "urls": set_default(broken_urls),
    }

    save_report(report)


def init(base_url, hostname, limit=0, restrict=True, snap=False):
    urls_queue = deque([base_url])

    processed_urls = set()
    local_urls = set()
    foreign_urls = set()
    broken_urls = set()

    if snap:
        if not path.exists("snaps/"):
            mkdir("snaps")

    while any(urls_queue):
        if len(processed_urls) >= limit and limit != 0:
            break

        current_url = urls_queue.popleft()
        processed_urls.add(current_url)

        print(f"Current URL: {current_url}")
        print(f"Queue size {len(urls_queue)}")

        try:
            response = requests.get(current_url)
        except (ConnectionError, InvalidURL, InvalidSchema, MissingSchema):
            broken_urls.add(current_url)
            continue

        if "Content-Type" in response.headers:
            content_type = response.headers.get("Content-Type", None)
            if content_type is None or "text/html" not in content_type:
                continue

        soup = bs(response.text, "html.parser")
        anchor_tags = soup.find_all("a")

        if snap:
            save_snap(current_url, soup)

        for anchor in anchor_tags:
            attr = anchor.attrs.get("href") if "href" in anchor.attrs else None
            url = urljoin(base_url, attr)

            if hostname in url:
                local_urls.add(url)
            else:
                foreign_urls.add(url)

        for local_url in local_urls:
            if local_url not in urls_queue and local_url not in processed_urls:
                urls_queue.append(local_url)

    generate_report(processed_urls, local_urls, foreign_urls, broken_urls)
