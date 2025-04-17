'''
@author: Krisna Pranav
@filename: cookie_repository.py
@date: 17 April 2025
'''

import os
import pickle
import time
from . import settings
from requests.cookies import RequestsCookieJar
from typing import Optional

class Error(Exception):
    pass

class LinkedinSessionExpired(Error):
    pass

class CookieRepository(object):
    def __init__(self, cookies_dir=settings.COOKIE_PATH):
        self.cookies_dir = cookies_dir or settings.COOKIE_PATH

    def save(self, cookies, username):
        self._ensure_cookies_dir()
        cookiejar_filepath = self._get_cookies_filepath(username)
        with open(cookiejar_filepath, "wb") as f:
            pickle.dump(cookies, f)


    def get(self, username: str) -> Optional[RequestsCookieJar]:
        cookies = self._load_cookies_from_cache(username)
        if cookies and not CookieRepository._is_token_still_valid(cookies):
            raise LinkedinSessionExpired

        return cookies

    def _ensure_cookies_dir(self):
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)

    def _get_cookies_filepath(self, username) -> str:
        return "{}{}.jr".format(self.cookies_dir, username)

    def _load_cookies_from_cache(self, username: str) -> Optional[RequestsCookieJar]:
        cookiejar_filepath = self._get_cookies_filepath(username)

        try:
            with open(cookiejar_filepath, "rb") as f:
                cookies = pickle.load(f)
                return cookies
        except FileNotFoundError:
            return None

    @staticmethod
    def _is_token_stil_valid(cookiejar: RequestsCookieJar):