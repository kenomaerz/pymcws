import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
import logging
from xml.etree import ElementTree
import urllib
from datetime import datetime, timedelta
from .exceptions import UnresolvableKeyError


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
        self.fields = None
        if self.key_id == "localhost":
            self.local_ip_list = "127.0.0.1"
            self.local_ip = "127.0.0.1"
            self.port = "52199"
            self.con_strategy = "local"
            self.fields = library_fields(self)

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
                self.fields = library_fields(self)
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
            self.fields = library_fields(self)
            return True
        # 4) Test if remote ip is reachable
        if self.test_remote():
            self.con_strategy = "remote"
            logger.debug(
                "Access key '" + self.key_id + "': con_strategy set to 'remote'."
            )
            self.fields = library_fields(self)
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
            except requests.exceptions.RequestException as e:
                logger.warn("Failed to connect to local ip: " + self.local_ip)

        return False

    def test_remote(self) -> bool:
        try:
            endpoint = self.address_remote() + "Alive"
            r = requests.get(endpoint, timeout=3, auth=self.credentials())
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException as e:
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
        self.https_port = et.find("https_port").text
        self.mac_address_list = et.find("macaddresslist").text.split(",")
        self.last_connection = datetime.now()

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
        self.lastConnection = datetime.now()
        return r


class Zone:
    """Zones represent targets for playback-related commands.

    Zones are available on a per-server basis and can be retrieved for each
    using MCWS. If you know the id or name of the zone that you want to target,
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
        """ Returns the type of the best identifier.

        Used in conjunction with best_identifier() to automatically determine
        the best strategy to communicate zones to the MCWS API.
        """
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


def library_fields(self: MediaServer):
    response = self.send_request("Library/Fields", {})
    response.raise_for_status()
    result = {}

    # Some fields are not reported by the library fields function
    result["Key"] = {
        "Name": "Key",
        "DataType": "Integer",
        "EditType": "Not editable",
        "Decoder": lambda x: int(x),
    }
    result["Date (readable)"] = {
        "Name": "Date (readable)",
        "DataType": "String",
        "EditType": "Not editable",
        "Decoder": lambda x: x,
    }

    root = ElementTree.fromstring(response.content)
    for item in root:
        name = item.attrib["Name"]
        data_type = item.attrib["DataType"]
        result[name] = {
            "Name": name,
            "DataType": data_type,
            "EditType": item.attrib["EditType"],
        }

        expression = item.attrib.get("Expression", None)
        if expression is not None:
            result[name]["Expression"] = expression

        if (
            data_type == "String"
            or data_type == "Path"
            or data_type == "User"
            or data_type == "Image File"
        ):
            result[name]["Decoder"] = lambda x: x
        elif data_type == "Integer" or data_type == "File Size":
            result[name]["Decoder"] = lambda x: int(x)
        elif data_type == "Date (float)":
            result[name]["Decoder"] = lambda x: parse_jriver_date(x)
        elif data_type == "Date":
            result[name]["Decoder"] = lambda x: datetime.fromtimestamp(int(x))
        elif data_type == "List":
            result[name]["Decoder"] = lambda x: x.split(";")
        elif data_type == "Decimal" or data_type == "Percentage" or data_type == "Time":
            result[name]["Decoder"] = lambda x: float(x.replace(",", "."))
        else:
            result[name]["Decoder"] = lambda x: x
    return result


def parse_jriver_date(jriver_date) -> datetime:
    """ Takes a jriver date float and turns it into a date object
    """
    if jriver_date is None:
        return None
    # Handle locale if necessary
    jriver_date = jriver_date.replace(",", ".")
    days = float(jriver_date)
    # JRiver returns days since midnight 30th december 1899, must convert
    # See https://yabb.jriver.com/interact/index.php/topic,123431.0.html
    date = datetime.strptime("30.12.1899", "%d.%m.%Y")
    date += timedelta(days=days)
    return date
