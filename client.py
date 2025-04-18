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
    LINKEDIN_BASE_URL = "https://www.linkedin.com"
    API_BASE_URL = f"{LINKEDIN_BASE_URL}/voyager/api"
    REQUEST_HEADERS = {
        "user-agent": " ".join(
            [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5)",
                "AppleWebKit/537.36 (KHTML, like Gecko)",
                "Chrome/83.0.4103.116 Safari/537.36",
            ]
        ),

        "accept-language": "en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
        "x-li-lang": "en_US",
        "x-restli-protocol-version": "2.0.0",
    }

    AUTH_REQUEST_HEADERS = {
        "X-Li-User-Agent": "LIAuthLibrary:0.0.3 com.linkedin.android:4.1.881 Asus_ASUS_Z01QD:android_9",
        "User-Agent": "ANDROID OS",
        "X-User-Language": "en",
        "X-User-Locale": "en_US",
        "Accept-Language": "en-us",
    }

    def __init__(
        self, *, debug=False, refresh_cookies=False, proxies={}, cookies_dir: str = ""
    ):
        self.session = requests.session()
        self.session.proxies.update(proxies)
        self.session.headers.update(Client.REQUEST_HEADERS)
        self.proxies = proxies
        self.logger = logger
        self.metadata = {}
        self._use_cookie_cache = not refresh_cookies
        self._cookie_repository = CookieRepository(cookies_dir=cookies_dir)

        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    def _request_session_cookies(self):
        self.logger.debug("Requesting new cookies.")

        res = requests.get(
            f"{Client.LINKEDIN_BASE_URL}/uas/authenticate",
            headers=Client.AUTH_REQUEST_HEADERS,
            proxies=self.proxies,
        )
        return res.cookies

    def _set_session_cookies(self, cookies: RequestsCookieJar):
        self.session.cookies = cookies
        self.session.headers["csrf-token"] = self.session.cookies["JSESSIONID"].strip(
            '"'
        )

    @property
    def cookies(self):
        return self.session.cookies

    def authenticate(self, username: str, password: str):
        if self._use_cookie_cache:
            self.logger.debug("Attempting to use cached cookies")
            cookies = self._cookie_repository.get(username)
            if cookies:
                self.logger.debug("Using cached cookies")
                self._set_session_cookies(cookies)
                self._fetch_metadata()
                return

        self._do_authentication_request(username, password)
        self._fetch_metadata()

    def _fetch_metadata(self):
        res = requests.get(
            f"{Client.LINKEDIN_BASE_URL}",
            cookies=self.session.cookies,
            headers=Client.AUTH_REQUEST_HEADERS,
            proxies=self.proxies,
        )

        soup = BeautifulSoup(res.text, "lxml")

        clientApplicationInstanceRaw = soup.find(
            "meta", attrs={"name": "applicationInstance"}
        )
        if clientApplicationInstanceRaw and isinstance(
            clientApplicationInstanceRaw, Tag
        ):
            clientApplicationInstanceRaw = clientApplicationInstanceRaw.attrs.get(
                "content", {}
            )
            clientApplicationInstance = json.loads(clientApplicationInstanceRaw)
            self.metadata["clientApplicationInstance"] = clientApplicationInstance

        clientPageInstanceIdRaw = soup.find(
            "meta", attrs={"name": "clientPageInstanceId"}
        )
        if clientPageInstanceIdRaw and isinstance(clientPageInstanceIdRaw, Tag):
            clientPageInstanceId = clientPageInstanceIdRaw.attrs.get("content", {})
            self.metadata["clientPageInstanceId"] = clientPageInstanceId

    def _do_authentication_request(self, username: str, password: str):
        self._set_session_cookies(self._request_session_cookies())

        payload = {
            "session_key": username,
            "session_password": password,
            "JSESSIONID": self.session.cookies["JSESSIONID"],
        }

        res = requests.post(
            f"{Client.LINKEDIN_BASE_URL}/uas/authenticate",
            data=payload,
            cookies=self.session.cookies,
            headers=Client.AUTH_REQUEST_HEADERS,
            proxies=self.proxies,
        )

        data = res.json()

        if data and data["login_result"] != "PASS":
            raise ChallengeException(data["login_result"])

        if res.status_code == 401:
            raise UnauthorizedException()

        if res.status_code != 200:
            raise Exception()

        self._set_session_cookies(res.cookies)
        self._cookie_repository.save(res.cookies, username)