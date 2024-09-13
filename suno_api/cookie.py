import os
import time
from http.cookies import SimpleCookie
from threading import Thread, Lock
import logging
import requests
from suno_api.client_api import COMMON_HEADERS


class SunoCookie:
    _instance = None  # Store the singleton instance
    _lock = Lock()    # To make it thread-safe

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(SunoCookie, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Avoid reinitializing the instance
            self.cookie = SimpleCookie()
            self.session_id = None
            self.token = None
            self._token_lock = Lock()  # Lock for token access
            self.initialized = True

    def load_cookie(self, cookie_str):
        if cookie_str:
            self.cookie.load(cookie_str)
            logging.info(f"Cookies loaded: {self.get_cookie()}")
        else:
            logging.warning('No cookie string provided to load.')

    def get_cookie(self):
        return ";".join([f"{i}={self.cookie.get(i).value}" for i in self.cookie.keys()])

    def set_session_id(self, session_id):
        self.session_id = session_id
        logging.info(f"Session ID set to: {self.session_id}")

    def get_session_id(self):
        return self.session_id

    def get_token(self):
        with self._token_lock:  # Ensure thread-safe access to the token
            logging.info(f"Token retrieved: {self.token}")
            return self.token
    
    def set_token(self, token: str):
        if token:
            with self._token_lock:  # Ensure thread-safe access to the token
                self.token = token
                logging.info(f"Token set to: {self.token}")
        else:
            logging.warning("Attempted to set a None token")


def update_token(suno_cookie: SunoCookie):
    headers = {"cookie": suno_cookie.get_cookie()}
    headers.update(COMMON_HEADERS)
    session_id = suno_cookie.get_session_id()

    try:
        # Make the request to get the token
        resp = requests.post(
            url=f"https://clerk.suno.com/v1/client/sessions/{session_id}/tokens?_clerk_js_version=4.72.0-snapshot.vc141245",
            headers=headers,
        )

        logging.info(f"Response status code: {resp.status_code}")
        
        if resp.status_code == 200:
            resp_headers = dict(resp.headers)
            set_cookie = resp_headers.get("Set-Cookie")
            if set_cookie:
                suno_cookie.load_cookie(set_cookie)
            else:
                logging.warning("No Set-Cookie found in response headers")

            # Retrieve and set the token
            token = resp.json().get("jwt")
            if token:
                logging.info(f"Token retrieved successfully: {token}")
                suno_cookie.set_token(token)  # Ensure token is set correctly
            else:
                logging.warning("Token not found in response JSON")
        else:
            logging.error(f"Failed to update token, status code: {resp.status_code}")

    except requests.RequestException as e:
        logging.error(f"Error during token update: {e}")


keep_alive_thread = None


def keep_alive(suno_cookie: SunoCookie):
    while True:
        try:
            update_token(suno_cookie)
        except Exception as e:
            logging.error(f"Error in keep_alive: {e}")
        finally:
            time.sleep(5)


def start_keep_alive(suno_cookie: SunoCookie):
    global keep_alive_thread
    if keep_alive_thread is None or not keep_alive_thread.is_alive():
        keep_alive_thread = Thread(target=keep_alive, args=(suno_cookie,))
        keep_alive_thread.start()
        logging.info("Keep alive thread started.")
    else:
        logging.info("Keep alive thread already running.")


suno_auth = SunoCookie()

suno_auth.set_session_id(os.getenv("SESSION_ID"))
suno_auth.load_cookie(os.getenv("COOKIE"))

update_token(suno_auth)

start_keep_alive(suno_auth)
