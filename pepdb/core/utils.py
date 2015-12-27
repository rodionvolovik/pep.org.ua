# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import os.path
import requests
import urllib2
import httplib2
from string import capwords
from datetime import datetime

from django.conf import settings

from oauth2client.client import SignedJwtAssertionCredentials
from dateutil import parser
from rfc6266 import parse_requests_response
from django.utils import translation
import gspread


def expand_gdrive_download_url(url):
    """
    Converts google drive links like
    https://drive.google.com/file/d/BLAHBLAH/view?usp=sharing
    to links that can be used for direct download from gdrive with requests
    """

    m = re.search(r"file\/d\/([^\/]+)\/", url)
    if m:
        return "https://docs.google.com/uc?export=download&id=%s" % m.group(1)

    m = re.search(r"open\?id=([^&]+)", url)
    if m:
        return "https://docs.google.com/uc?export=download&id=%s" % m.group(1)

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
        s = unicode(s).strip()
        if s == "-" or not s:
            return None

        return parser.parse(s, default=datetime(1970, 1, 1)).date()
    except ValueError:
        return None


class CSVDownloadClient(object):
    """
    Class to quickly export google spreadsheet into CSV and download it
    Currently not in use
    """
    def __init__(self, auth_key=getattr(settings, "GAUTH_CREDENTIALS", None)):
        super(CSVDownloadClient, self).__init__()
        self.auth_key = auth_key

    def get_auth_token(self):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SignedJwtAssertionCredentials(
            self.auth_key['client_email'], self.auth_key['private_key'], scope)

        credentials.refresh(httplib2.Http())
        return credentials.token_response["access_token"]

    def download(self, spreadsheet=getattr(settings, "SPREADSHEET_ID", None),
                 gid=0, format="csv"):
        url_format = ("https://spreadsheets.google.com/feeds/download/"
                      "spreadsheets/Export?key=%s&exportFormat=%s&gid=%i")
        headers = {
            "Authorization": "Bearer " + self.get_auth_token()
        }
        req = urllib2.Request(url_format % (spreadsheet, format, gid),
                              headers=headers)

        return urllib2.urlopen(req)


def get_spreadsheet(auth_key=getattr(settings, "GAUTH_CREDENTIALS", None),
                    spreadsheet=getattr(settings, "SPREADSHEET_ID", None)):
    """
    Helper to authenticate on google drive and obtain spreadsheet object
    """

    credentials = SignedJwtAssertionCredentials(
        auth_key['client_email'], auth_key['private_key'],
        ['https://spreadsheets.google.com/feeds'])

    credentials.refresh(httplib2.Http())

    gc = gspread.authorize(credentials)
    return gc.open_by_key(spreadsheet)


def is_cyr(name):
    return re.search("[а-яіїєґ]+", name.lower(), re.UNICODE) is not None


def is_ukr(name):
    return re.search("['іїєґ]+", name.lower(), re.UNICODE) is not None


def parse_fullname(person_name):
    # Extra care for initials (especialy those without space)
    person_name = re.sub("\s+", " ",
                         person_name.replace(".", ". ").replace('\xa0', " "))

    chunks = person_name.strip().split(" ")

    last_name = ""
    first_name = ""
    patronymic = ""

    if len(chunks) == 2:
        last_name = title(chunks[0])
        first_name = title(chunks[1])
    elif len(chunks) > 2:
        last_name = title(" ".join(chunks[:-2]))
        first_name = title(chunks[-2])
        patronymic = title(chunks[-1])

    return last_name, first_name, patronymic


class TranslatedField(object):
    def __init__(self, ua_field, en_field):
        self.ua_field = ua_field
        self.en_field = en_field

    def __get__(self, instance, owner):
        if translation.get_language() == 'en':
            return getattr(instance, self.en_field)
        else:
            return getattr(instance, self.ua_field)


VALID_POSITIONS = [
    "син",
    "дружина",
    "чоловік",
    "донька",
    "дочка",
    "мати",
    "батько",
    "жінка",
    "брат",
    "дружина брата",
    "сестра",
    "теща",
    "онук",
    "мама",
    "невістка",
    "племінник",
    "баба",
    "пасинок",
    "дитина",
    "матір",
    "онука",
    "зять",
    "діти",
    "свекор",
    "бабуся",
    "племінниця",
    "донечка",
    "тесть",
    "внучка",
    "сын",
    "чоловик",
    "співмешканець",
    "супруга",
    "допька",
    "дружіна",
    "падчерка",
    "внук",
    "свекруха",
    "мать",
    "доч",
    "батьки",
    "тітка",
    "співмешканака",
    "онучка",
    "тато",
    "жена",
]

RELATIONS_MAPPING = {
    "подружжя": "чоловік/дружина",
    "батьки": "батько/мати",
    "дитина": "син/дочка",
    "онук": "внук",
    "брат": "рідний брат",
    "інше": "особисті зв'язки",
    "син": "син",
    "дружина": "дружина",
    "чоловік": "чоловік",
    "донька": "дочка",
    "дочка": "дочка",
    "мати": "мати",
    "батько": "батько",
    "жінка": "дружина",
    "брат": "брат",
    "дружина брата": "особисті зв'язки",
    "сестра": "рідна сестра",
    "теща": "особисті зв'язки",
    "онук": "внук",
    "мама": "мати",
    "невістка": "особисті зв'язки",
    "племінник": "особисті зв'язки",
    "баба": "баба",
    "пасинок": "усиновлений",
    "дитина" "син/дочка"
    "матір": "мати",
    "онука": "внучка",
    "зять": "особисті зв'язки",
    "діти": "син/дочка",
    "свекор": "особисті зв'язки",
    "бабуся": "баба",
    "племінниця": "особисті зв'язки",
    "донечка": "дочка",
    "тесть": "особисті зв'язки",
    "внучка": "внучка",
    "сын": "син",
    "чоловик": "чоловік",
    "співмешканець": "особи, які спільно проживають",
    "супруга": "дружина",
    "допька": "дочка",
    "дружіна": "дружина",
    "падчерка": "усиновлена",
    "внук": "внук",
    "свекруха": "особисті зв'язки",
    "мать": "мати",
    "доч": "дочка",
    "батьки": "батько/мати",
    "тітка": "особисті зв'язки",
    "співмешканака": "особи, які спільно проживають",
    "онучка": "внучка",
    "тато": "батько",
    "жена": "дружина"
}


def parse_family_member(s):
    try:
        position, person = s.split(None, 1)
        if "-" in position:
            position, person = s.split("-", 1)

        position = position.strip(u" -—,.:").lower()
        person = person.strip(u" -—,")

        if position not in VALID_POSITIONS:
            raise ValueError

        for pos in VALID_POSITIONS:
            if person.lower().startswith(pos):
                raise ValueError

        return {
            "relation": position,
            "name": person
        }
    except ValueError:
        return None
