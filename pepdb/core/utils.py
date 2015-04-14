import re
import os.path
import requests
from string import capwords
from datetime import datetime

from dateutil import parser
from rfc6266 import parse_requests_response


def expand_gdrive_download_url(url):
    """
    Converts google drive links like
    https://drive.google.com/file/d/BLAHBLAH/view?usp=sharing
    to links that can be used for direct download from gdrive with requests
    """

    m = re.search(r"file\/d\/([^\/]+)\/", url)
    if m:
        return "https://docs.google.com/uc?export=download&id=%s" % m.group(1)
    else:
        return url


def download(url):
    """
    Downloads from url, extracts filename from url or content disposition
    Returns original fname, sanitized one and content of file
    Or None, None, None
    """
    resp = requests.get(url)

    if resp.status_code == 200:
        parsed = parse_requests_response(resp)
        fname = parsed.filename_sanitized(
            os.path.splitext(parsed.filename_unsafe)[-1].strip("."))

        return parsed.filename_unsafe, fname, resp.content
    else:
        return None, None, None


def title(s):
    chunks = s.split()
    chunks = map(lambda x: capwords(x, u"-"), chunks)
    return u" ".join(chunks)


def parse_date(s):
    try:
        if s == "-" or not s:
            return None

        return parser.parse(s, default=datetime(1970, 1, 1)).date()
    except ValueError:
        return None
