from pymcws.model import MediaFile
from datetime import datetime, timedelta
from xml.etree import ElementTree

# JRiver dates are days since midnight 30th december 1899
# See https://yabb.jriver.com/interact/index.php/topic,123431.0.html
reference_date = datetime.strptime("30.12.1899", "%d.%m.%Y")


def transform_semistructured_response(
    response, header_items: int, group_prefix: str, group_size: int
) -> list:
    """Converts the relatively unstructured XML responses from MCWS into
    a list of dictionaries that is easier to process. This method assumes that after a few
    leading entries, a sequence of entries that share a common prefix repeat and
    should be grouped as items. An example is the response from Library/List:
    http://localhost:52199/MCWS/v1/Library/List

    The result is a list, that at index 0 contains a dictionary containing the header items,
    and afterwards dictionaries that contain the items.

    Note: This method makes use of the fact that dictionaries return their entries in order since Python 3.6
    """
    result = []
    items = list(transform_unstructured_response(response).items())
    header = {}
    for item in items[:header_items]:
        header[item[0]] = item[1]
    result.append(header)

    items = items[header_items:]
    chunks = [items[i : i + group_size] for i in range(0, len(items), group_size)]
    i = 0
    for chunk in chunks:
        group = {}
        for item in chunk:
            key = item[0][len(group_prefix + str(i)) :]
            if len(key) == 0:
                key = group_prefix
            group[key] = item[1]
        result.append(group)
    return result


def transform_unstructured_response(response, try_int_cast: bool = False):
    """Converts the relatively unstructured XML responses from MCWS into
    a dictionary that is easier to process.
    """
    result = {}
    root = ElementTree.fromstring(response.content)
    for child in root:
        result[child.attrib["Name"]] = child.text
    if try_int_cast:
        for key in result:
            try:
                result[key] = int(result[key])
            except ValueError:
                pass  # passing is ok: If untranslatable, leave alone
    return result


def transform_list_response(response):
    """ Transforms a response containing a list of items into a list of strings.
    """
    result = []
    root = ElementTree.fromstring(response.content)
    for item in root:
        result.append(item.text)
    return result


def transform_mpl_response(media_server, response):
    """ Transforms an MPL response into a list of dictionaries.

    Each dictionary represents one file and contains the fields as keys.
    """
    result = []
    root = ElementTree.fromstring(response.content)
    for item in root:
        tags = {}
        for tag in item:
            name = tag.attrib["Name"]
            tags[name] = media_server.fields[name]["Decoder"](tag.text)
        result.append(MediaFile(media_server, tags))
    return result


def escape_for_query(query_part: str) -> str:
    """Escapes all characters reserved by jriver in a natural string.

    Do not put a complete query in here - this method is used to escape
    reserved characters in a natural string that will be used as a query fragment.
    This is usually the content of a field (e.g. an album or artist name).
    """
    query_part = query_part.replace('"', '/"')
    query_part = query_part.replace("^", "/^")
    query_part = query_part.replace("[", "/[")
    query_part = query_part.replace("]", "/]")
    return query_part


def serialize_file_list(files: list, active_item_index: int = -1):
    """ Returns a serialized file list, which JRiver requires in some API calls.
        These are a not documented further, but form a string of comma seperated values.
        These are, in order:
        [0] The value '2', stating a serialization version. Only 2 is supported these days.
        [1] The number of included keys
        [2] The active element (?), -1 for none
        [3]..[len(files + 3)]: The keys of the files.
    """
    result = "2;" + str(len(files)) + ";" + str(active_item_index)
    for file in files:
        result += ";" + str(file["Key"])
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
    return reference_date + timedelta(days=days)


def serialize_jriver_date(date: datetime) -> str:
    """ Takes a jriver date float and turns it into a date object
    """
    if date is None:
        return None
    delta = date - reference_date
    return str(delta.days)
