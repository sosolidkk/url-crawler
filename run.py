import argparse
import json
from collections import deque
from os import mkdir, path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup as bs
from requests.exceptions import (
    ConnectionError,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
)


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


def str2bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif value.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def cli_args():
    description = "A program to scrape site URLs and download its content as .html or save the URLs as JSON"
    args = argparse.ArgumentParser(description=description)

    args.add_argument(
        "--url",
        "-u",
        help="Start point website to be mapped, i.e 'http://example.org'",
        required=True,
    )

    args.add_argument(
        "--limit",
        "-l",
        default=0,
        help="Limit the number of foreign urls. 0 to unlimited",
        required=False,
        type=int,
    )

    args.add_argument(
        "--snap",
        "-s",
        default=False,
        help="Save each url page on a .html file. i.e 'snapshot/url-path.html'. By default is False",
        nargs="?",
        required=False,
        type=str2bool,
    )

    args.add_argument(
        "--restrict",
        "-r",
        const=True,
        default=True,
        help="Restric search to it's original domain URL. By default is True",
        nargs="?",
        required=False,
        type=str2bool,
    )

    return args


if __name__ == "__main__":
    args = vars(cli_args().parse_args())

    base_url = args.get("url", None)
    hostname = urlparse(base_url).hostname

    limit = args.get("limit", None)
    restrict = args.get("restrict", None)
    snap = args.get("snap", None)

    print("-------------------------------------------")
    print(f"Base url: {base_url}\nHostname: {hostname}")
    print(f"Limit of processed URLs: {limit}")
    print(f"Restrict search to it's original domain URL: {restrict}")
    print(f"Save snap of every processed URL: {snap}")
    print("-------------------------------------------\n")

    init(base_url, hostname, limit, restrict, snap)

    print("Finished! Created report.json file with insights.")
