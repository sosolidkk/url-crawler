from urllib.parse import urlparse

from src.args import cli_args
from src.crawl import init

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
