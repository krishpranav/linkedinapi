'''
@author: Krisna Pranav
@filename: client.py
@date: 17 April 2025
'''

import requests
import logging
from cookie_repository import CookieRepository
from bs4 import BeautifulSoup, Tag
from requests.cookies import RequestsCookieJar
import json

logger = logging.getLogger(__name__)

class ChallengeException(Exception):
    pass

class UnauthorizedException(Exception):
    pass

class Client(object):
    LINKEDIN_BASE_URL = "https://www.linkedin.com/"