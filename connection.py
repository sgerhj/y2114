import logging
from base64 import b64encode
from time import sleep
import requests
import urllib3
import chardet
import lolbot.common.config as config

class Connection:
    """Handles HTTP requests for Riot Client and League Client"""

    LCU_HOST = '127.0.0.1'
    RCU_HOST = '127.0.0.1'
    LCU_USERNAME = 'riot'
    RCU_USERNAME = 'riot'

    def __init__(self) -> None:
        self.client_type = ''
        self.client_username = ''
        self.client_password = ''
        self.procname = ''
        self.pid = ''
        self.host = ''
        self.port = ''
        self.protocol = ''
        self.headers = ''
        self.session = requests.session()
        self.config = config.ConfigRW()
        self.log = logging.getLogger(__name__)
        logging.getLogger('urllib3').setLevel(logging.INFO)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def read_file_with_detected_encoding(self, file_path):
        """Reads file with detected encoding"""
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            if encoding is None:
                raise ValueError("Could not detect encoding")
            return raw_data.decode(encoding)

    def set_rc_headers(self) -> None:
        """Sets header info for Riot Client"""
        self.log.debug("Initializing Riot Client session")
        self.host = Connection.RCU_HOST
        self.client_username = Connection.RCU_USERNAME

        try:
            data = self.read_file_with_detected_encoding(config.Constants.RIOT_LOCKFILE)
        except FileNotFoundError:
            self.log.error("Riot lockfile not found")
            return
        except (UnicodeDecodeError, ValueError) as e:
            self.log.error(f"Error reading lockfile: {e}")
            return

        self.log.debug(data)
        data = data.split(':')
        self.procname = data[0]
        self.pid = data[1]
        self.port = data[2]
        self.client_password = data[3]
        self.protocol = data[4]

        # headers
        userpass = b64encode(bytes('{}:{}'.format(self.client_username, self.client_password), 'utf-8')).decode('ascii')
        self.headers = {'Authorization': 'Basic {}'.format(userpass), "Content-Type": "application/json"}
        self.log.debug(self.headers['Authorization'])

    def set_lcu_headers(self, verbose: bool = True) -> None:
        """Sets header info for League Client"""
        self.host = Connection.LCU_HOST
        self.client_username = Connection.LCU_USERNAME

        try:
            data = self.read_file_with_detected_encoding(self.config.get_data('league_lockfile'))
        except FileNotFoundError:
            self.log.error("League lockfile not found")
            return
        except (UnicodeDecodeError, ValueError) as e:
            self.log.error(f"Error reading lockfile: {e}")
            return

        self.log.debug(data)
        data = data.split(':')
        self.procname = data[0]
        self.pid = data[1]
        self.port = data[2]
        self.client_password = data[3]
        self.protocol = data[4]

        # headers
        userpass = b64encode(bytes('{}:{}'.format(self.client_username, self.client_password), 'utf-8')).decode('ascii')
        self.headers = {'Authorization': 'Basic {}'.format(userpass)}
        self.log.debug(self.headers['Authorization'])

    def connect_lcu(self, verbose: bool = True) -> None:
        """Tries to connect to league client"""
        if verbose:
            self.log.info("Connecting to LCU API")
        else:
            self.log.debug("Connecting to LCU API")
        self.host = Connection.LCU_HOST
        self.client_username = Connection.LCU_USERNAME

        try:
            data = self.read_file_with_detected_encoding(self.config.get_data('league_lockfile'))
        except FileNotFoundError:
            self.log.error("League lockfile not found")
            return
        except (UnicodeDecodeError, ValueError) as e:
            self.log.error(f"Error reading lockfile: {e}")
            return

        self.log.debug(data)
        data = data.split(':')
        self.procname = data[0]
        self.pid = data[1]
        self.port = data[2]
        self.client_password = data[3]
        self.protocol = data[4]

        # headers
        userpass = b64encode(bytes('{}:{}'.format(self.client_username, self.client_password), 'utf-8')).decode('ascii')
        self.headers = {'Authorization': 'Basic {}'.format(userpass)}
        self.log.debug(self.headers['Authorization'])

        # connect
        for i in range(30):
            sleep(1)
            try:
                r = self.request('get', '/lol-login/v1/session')
                self.log.debug(f"Connection attempt {i+1}: {r.json()}")
            except Exception as e:
                self.log.error(f"Error during connection attempt {i+1}: {e}")
                continue
            if r.json().get('state') == 'SUCCEEDED':
                if verbose:
                    self.log.info("Connection Successful")
                else:
                    self.log.debug("Connection Successful")
                self.request('post', '/lol-login/v1/delete-rso-on-close')  # ensures self.logout after close
                sleep(2)
                return
        raise Exception("Could not connect to League Client")

    def request(self, method: str, path: str, query: str = '', data: dict = None) -> requests.models.Response:
        """Handles HTTP requests to Riot Client or League Client server"""
        if data is None:
            data = {}
        if not query:
            url = "{}://{}:{}{}".format(self.protocol, self.host, self.port, path)
        else:
            url = "{}://{}:{}{}?{}".format(self.protocol, self.host, self.port, path, query)

        self.log.debug("{} {} {}".format(method.upper(), url, data))

        fn = getattr(self.session, method)

        if not data:
            r = fn(url, verify=False, headers=self.headers)
        else:
            r = fn(url, verify=False, headers=self.headers, json=data)
        return r
