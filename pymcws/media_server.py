import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
import logging
from xml.etree import ElementTree
import urllib
from datetime import datetime
from pymcws.exceptions import UnresolvableKeyError
from pymcws.server_mixins import Library, Playback, File, Files, Recipes
from pymcws.api.library import fields as lib_fields


URL_KEYLOOKUP = "http://webplay.jriver.com/libraryserver/lookup"
URL_API = "http://{ip}:{port}/MCWS/v1/"

logger = logging.getLogger(__name__)


class MediaServer:
    def __init__(self, key_id: str, user: str, password: str):
        """Creates an access key and stores data relevant to this key.

        Minimally, the key_id is required. If either username or password is
        'None', then all requests to the server behind this key will be sent
        without authentication. Use the key_id "localhost" to directly connect
        to the jriver instance running on the same machine as the code.
        """

        self.key_id = key_id
        self.user = user
        self.password = password
        self.con_strategy = "unknown"
        self.session = requests.Session()
        self.session.auth = (user, password)
        self.__fields = None
        if self.key_id == "localhost":
            self.local_ip_list = "127.0.0.1"
            self.local_ip = "127.0.0.1"
            self.port = "52199"
            self.con_strategy = "local"

    @property
    def fields(self, update: bool = False):
        """ Contains the fields available on this server and their definitions.

            This is loaded lazily and chached in the server for type conversion
            in order to avoid unnecessary queries to the server. To update the
            cache, call this function with update = True.
        """
        if self.__fields is None or update:
            self.__fields = lib_fields(self)
        return self.__fields

    def __str__(self):
        return "Server " + self.key_id + " at " + self.address()

    def credentials(self) -> HTTPBasicAuth:
        """ Retrieves the credentials for this instance in form of a
        HTTPBasicAuth object
        """
        if self.user is None or self.password is None:
            return None
        else:
            return HTTPBasicAuth(self.user, self.password)

    def refresh(self) -> bool:
        """ Identifies the best way to connect to the machine behind the key,
        querying data from jriver web service if necessary.
        Returns true if successful and false otherwise.

        This function does the following:
        # 1) Test if local ip is present and reachable, if true sets connection
             strategy to local and exists
        # 2) Query jriver service for key data, update keyData accordingly
        # 3) Test if local IP is reachable
        # 4) If not, test if remote ip is reachable
        # 5) else machine behind key is unreachable
        # 6) if machine is reachable, update the field list
        """
        logger.debug("Refreshing access key '" + self.key_id + "'")
        # 1) Test if local ip is present and reachable
        if self.con_strategy == "local":
            if self.test_local():
                self.con_strategy = "local"
                logger.debug(
                    "Access key '" + self.key_id + "': con_strategy set to 'local'."
                )
                return True
            else:
                self.con_strategy = "unknown"

        # 2) Test query jriver service for key data
        if self.con_strategy == "unknown" or self.con_strategy == "unreachable":
            logger.debug(
                "Access key '"
                + self.key_id
                + "' has con_strategy '"
                + self.con_strategy
                + "' - refreshing."
            )
            self.update_from_jriver()

        # 3) Test if local IP is reachable
        if self.test_local():
            self.con_strategy = "local"
            logger.debug(
                "Access key '" + self.key_id + "': con_strategy set to 'local'."
            )
            return True
        # 4) Test if remote ip is reachable
        if self.test_remote():
            self.con_strategy = "remote"
            logger.debug(
                "Access key '" + self.key_id + "': con_strategy set to 'remote'."
            )
            return True
        # 5) Machine behind key is unreachable
        return False

    def address(self):
        """ Returns the address of the mediaserver with regard to the currently chosen
            connection strategy. If no strategy was selected, None is returned.
        """
        if self.con_strategy == "local":
            return self.address_local()
        if self.con_strategy == "remote":
            return self.address_remote()
        return None

    def address_local(self):
        """ Returns the local address of the server.

            This method requires that exactly one local_ip is set.
            Call test_local to test which ip from the local_ip_list is working
            and set it automatically.
        """
        if self.local_ip is None or self.port is None:
            return None
        return URL_API.format(ip=self.local_ip, port=self.port)

    def address_remote(self):
        """ Returns the remote address of the server.

            Assuming that the server is configured correctly and reachable,
            this address should always work.
        """
        if self.remote_ip is None or self.port is None:
            return None
        return URL_API.format(ip=self.remote_ip, port=self.port)

    def test_local(self) -> bool:
        for ip in self.local_ip_list:
            try:
                self.local_ip = ip
                endpoint = self.address_local() + "Alive"
                r = requests.get(endpoint, timeout=2, auth=self.credentials())
                if r.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                logger.warn("Failed to connect to local ip: " + self.local_ip)

        return False

    def test_remote(self) -> bool:
        try:
            endpoint = self.address_remote() + "Alive"
            r = requests.get(endpoint, timeout=3, auth=self.credentials())
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            logger.warn("Failed to connect to remote ip: " + self.remote_ip)
        return False

    def update_from_jriver(self):
        """ Contacts the JRiver WebService to retrieve information about the access key.

        Updates the local instance with current data. This usually is called
        automatically in the refresh method and should not usually need to be called
        from outside the class, please consider reporting your usecase if you need to.
        """
        logger.debug("Updating access key '" + self.key_id + "'")
        r = requests.get(URL_KEYLOOKUP, params={"id": self.key_id}, timeout=5)
        r.raise_for_status()
        et = ElementTree.fromstring(r.content)
        if et.attrib["Status"] == "Error":
            logger.error("KeyID '" + self.key_id + "' could not be resolved.'")
            raise UnresolvableKeyError(self.key_id, et.find("msg").text)
        self.key_id = et.find("keyid").text
        self.ip = et.find("ip").text
        self.port = et.find("port").text
        self.local_ip_list = et.find("localiplist").text.split(",")
        self.remote_ip = et.find("ip").text
        self.http_port = et.find("port").text
        self.https_port = et.find("https_port")
        if self.https_port is not None:
            self.https_port = self.https_port.text
        self.mac_address_list = et.find("macaddresslist").text.split(",")
        self.last_connection = datetime.now()

    def send_request(self, extension: str, payload=None):
        if self.con_strategy == "unknown":
            self.refresh()

        # Clean None values from payload
        if payload is not None:
            for entry in list(payload.items()):
                if entry[1] is None:
                    payload.pop(entry[0])

        try:
            return self.attempt_request(extension, payload)
        except HTTPError:
            logger.warn(
                "Failed to contact " + self.key_id + " next failure will cause error."
            )
            self.refresh()
            # TODO Better retry handling
            # Currently, renegotiation happens ones, and fails if that fails
            # as well. Need to consider consequences and expand accordingly
            return self.attempt_request(extension, payload)

    def attempt_request(self, extension: str, payload=None):
        """Sends a request to the server specified in key_data

        Requires a filled-out key_data object. Will send a request to the server
        specified in key_data, addressing the endpoint with the payload.
        """

        # Get destination
        if self.address() is None:
            self.refresh()
        endpoint = self.address() + extension
        # prepare payload
        if payload is not None:
            params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
        else:
            params = None
        r = self.session.get(endpoint, params=params)

        if r.status_code == 404:
            r.raise_for_status()
        self.lastConnection = datetime.now()
        return r


class ApiMediaServer(MediaServer):
    def __init__(self, key_id: str, user: str, password: str):
        super().__init__(key_id, user, password)
        self.library = Library(self)
        self.playback = Playback(self)
        self.file = File(self)
        self.files = Files(self)
        self.recipes = Recipes(self)
