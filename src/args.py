import argparse


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
