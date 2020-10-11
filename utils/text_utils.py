import logging
import re

RE_TG_USERNAME = r"@(\w{5,32})"
RE_TG_URL_V1 = r".*t\.me\/(\w+)"
RE_TG_URL_V2 = r".*telegram\.me\/(\w+)"


def clean_entity_text(text):
    matches = re.findall(RE_TG_USERNAME, text)
    if matches:
        logging.debug('Cleaned text "' + text + '" to: @' + matches[0])
        return '@' + matches[0]
    logging.debug('Could not clean: ' + text)
    return None


def clean_entity_url(url):
    matches = re.findall(RE_TG_URL_V1,url)
    if matches and not matches[0]=='joinchat':
        logging.debug('cleaned url "' + url + '" to: @'+matches[0])
        return '@' + matches[0]

    matches = re.findall(RE_TG_URL_V2,url)
    if matches and not matches[0]=='joinchat':
        logging.debug('cleaned url "' + url + '" to: @'+matches[0])
        return '@' + matches[0]

    return None
