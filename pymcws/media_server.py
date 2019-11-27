import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
import logging
from xml.etree import ElementTree
import datetime
import urllib

from .exceptions import UnresolvableKeyError


URL_KEYLOOKUP = "http://webplay.jriver.com/libraryserver/lookup"
URL_LOCAL = "http://{ip}:{port}/MCWS/v1/"

logger = logging.getLogger(__name__)


class MediaServer:

    key_id = None
    ip = None
    port = None
    local_ip_list = None
    local_ip = None
    https_port = None
    mac_address_list = None
    con_strategy = "unknown"
    last_connection = None
    user = None
    password = None
    zones = None

    def __init__(self, key_id: str, user: str, password: str):
        """Creates an access key and stores data relevant to this key.

        Minimally, the key_id is required. If either username or password is
        'None', then all requests to the server behin this key will be sent
        without authentication. Use the key_id "localhost" to directly connect
        to the jriver instance running on the same machine as the code.
        """

        self.key_id = key_id
        self.user = user
        self.password = password
        if self.key_id == "localhost":
            self.local_ip_list = "127.0.0.1"
            self.port = "52199"
            self.con_strategy = "local"

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
        # 5) Machine behind key is unreachable
        return False

    def address(self):
        return self.address_local()

    def address_local(self):
        if self.local_ip is None or self.port is None:
            return None
        return URL_LOCAL.format(ip=self.local_ip, port=self.port)

    def address_remote(self):
        # TODO implement
        pass

    def configure_local_connection(self):
        # TODO
        pass

    def configure_remote_connection(self):
        # TODO
        pass

    def test_local(self) -> bool:
        for ip in self.local_ip_list:
            try:
                self.local_ip = ip
                endpoint = self.address_local() + "Alive"
                r = requests.get(endpoint, timeout=2, auth=self.credentials())
                if r.status_code == 200:
                    return True
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                logger.warn("Failed to connect to local ip: " + self.local_ip)

        return False

    def test_remote(self) -> bool:
        pass

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
        # TODO Need to detect and handle lists of IPs
        self.local_ip_list = et.find("localiplist").text.split(",")
        self.https_port = et.find("https_port").text
        self.mac_address_list = et.find("macaddresslist").text.split(",")
        self.last_connection = datetime.datetime.now()

    def send_request(self, extension: str, payload=None):
        if self.con_strategy == "unknown":
            self.refresh()
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
        # choose authentication strategy
        if self.user is None or self.password is None:
            r = requests.get(endpoint, params=params)
        else:
            r = requests.get(endpoint, params=params, auth=self.credentials())
        if r.status_code == 404:
            r.raise_for_status()
        self.lastConnection = datetime.datetime.now()
        return r


class Zone:
    """Zones represent targets for playback-related commands.

    Zones are available on a per-Server basis and can be retrieved for each
    using mcws. If you know the id or name of the zone that you want to target,
    you can also create a zone and set id, index or name manually. The missing
    fields do not affect functionality, the best available value is retrieved
    automatically.
    """

    def __init__(self):
        self.id = -1  # Default ID indicating the zone currently selected in MC
        self.index = None
        self.name = None
        self.guid = None
        self.is_dlna = None

    def best_identifier(self):
        """Checks available fields and retirves the best available.

        Use best_identifier_type() to find out what type of identifier was
        returned.
        """
        if self.id is not None:
            return self.id
        if self.name is not None:
            return self.name
        if self.index is not None:
            return self.index
        logger.warn(
            "Unable to determine best identifier "
            + " for Zone. This is probably a bug."
        )

    def best_identifier_type(self):
        if self.id is not None:
            return "ID"
        if self.name is not None:
            return "Name"
        if self.index is not None:
            return "Index"
        logger.warn(
            "Unable to determine best identifier type"
            + " for Zone. This is probably a bug."
        )

    def __str__(self):
        return self.name
