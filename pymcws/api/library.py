from pymcws.model import MediaFile
from pymcws.utils import (
    transform_semistructured_response,
    transform_list_response,
    transform_unstructured_response,
    parse_jriver_date,
    serialize_jriver_date,
)
import logging
from datetime import datetime
from xml.etree import ElementTree

logger = logging.getLogger(__name__)


def get_list(media_server, include_header=False):
    """ Returns a list of dictionaries containing the information of available libraries.

    The index in the list of libraries is the library id.
    This method diverges from the original API. Call library_get_default to get the default library.
    Additionally, you can use library_get_loaded to only return the loaded library.
    set the include_header flag to mimic original API behaviour and include a header index 0.
    See http://localhost:52199/MCWS/v1/Library/List for example.
    """
    response = media_server.send_request("Library/List")
    result = transform_semistructured_response(response, 2, "Library", 3)
    result[0]["DefaultLibrary"] = int(result[0]["DefaultLibrary"])
    result[0]["NumberOfLibraries"] = int(result[0]["NumberOfLibraries"])
    i = 0
    for library in result[1:]:
        library["Loaded"] = library["Loaded"] == "1"
        library["ID"] = i
        i += 1
    if not include_header:
        result.pop(0)
    return result


def get_default(media_server):
    """ Returns the information of the default library
    """
    libraries = get_list(media_server, True)
    default_id = libraries[0]["DefaultLibrary"]
    result = libraries[default_id + 1]
    result["id"] = default_id
    return result


def get_loaded(media_server):
    """ Returns the information of the currently library
    """
    libraries = get_list(media_server)
    for library in libraries:
        if library["Loaded"]:
            return library
    return None


def fields(media_server):
    """ Returns information about the library fields that this server can handle.

        The result is a dictionary that contains the name of all known fields as
        keys, and corresponding information as a dictionary with the keys:
        'Name', 'DataType', 'EditType' (all as provided by MCWS) and
        'Decoder', a lambda function that can parse values fo this field to the
        correct python type.
    """

    response = media_server.send_request("Library/Fields", {})
    response.raise_for_status()
    result = {}

    # Some fields are not reported by the library fields function
    result["Key"] = {
        "Name": "Key",
        "DataType": "Integer",
        "EditType": "Not editable",
        "Decoder": lambda x: int(x),
        "Encoder": lambda x: str(x),
    }
    result["Date (readable)"] = {
        "Name": "Date (readable)",
        "DataType": "String",
        "EditType": "Not editable",
        "Decoder": lambda x: x,
        "Encoder": lambda x: x,
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
            result[name]["Encoder"] = lambda x: '"' + x + '"'
        elif data_type == "Integer" or data_type == "File Size":
            result[name]["Decoder"] = lambda x: int(x)
            result[name]["Encoder"] = lambda x: str(x)
        elif data_type == "Date (float)":
            result[name]["Decoder"] = lambda x: parse_jriver_date(x)
            result[name]["Encoder"] = lambda x: serialize_jriver_date(x)
        elif data_type == "Date":
            result[name]["Decoder"] = lambda x: datetime.fromtimestamp(int(x))
            result[name]["Encoder"] = lambda x: str(datetime.timestamp(x))
        elif data_type == "List":
            result[name]["Decoder"] = lambda x: x.split(";")
            result[name]["Encoder"] = lambda x: '"' + ";".join(x) + '"'
        elif data_type == "Decimal" or data_type == "Percentage" or data_type == "Time":
            result[name]["Decoder"] = lambda x: float(x.replace(",", "."))
            result[name]["Encoder"] = lambda x: str(x)
        else:
            logger.warning(
                "Unhandled data type for field '"
                + name
                + "' found: "
                + data_type
                + ". Using identity to decode and encode."
            )
            result[name]["Decoder"] = lambda x: x
            result[name]["Encoder"] = lambda x: x
    return result


def values(
    media_server,
    filter: str = None,
    field: str = None,
    query: str = None,
    limit: str = None,
    version: int = 2,
):
    """ Get a list of values from the database (artists, albums, etc.).

        filter: None to get all values for a particular field, or some search to
                get matching values from any number of fields.
        field:  A comma-delimited list of fields as a string, or a list of strings
                to get values from (use None to search default fields).
        query:  A search to use to get the files to retrieve values from (use empty
                to use all imported files).
        limit: Maximum number of values to return.
        version: The version of the data used for results (2 is the newest version).

    """
    if isinstance(field, list):
        field = ",".join(field)
    payload = {
        "Filter": filter,
        "Field": field,
        "Files": query,
        "Limit": limit,
        "Version": version,
    }
    response = media_server.send_request("Library/Values", payload)
    response.raise_for_status()
    return transform_list_response(response)


def create_file(media_server) -> MediaFile:
    """ Creates a new file in the library. This file can then be populated with
        tag data and saved. Don't forget to set media type so it actually appears
        in JRiver.
    """
    response = media_server.send_request("Library/CreateFile")
    result = transform_unstructured_response(response)
    return MediaFile(media_server, result)
