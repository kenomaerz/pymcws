from .media_server import MediaServer, Zone

# import logging
from xml.etree import ElementTree
from PIL import Image
from io import BytesIO


def alive(media_server: MediaServer):
    response = media_server.send_request("Alive")
    return transform_unstructured_response(response)


#
#   PLAYBACK
#


def playback_play(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, "Play", zone)


def playback_playpause(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, "PlayPause", zone)


def playback_stop(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, "Stop", zone)


def playback_stopall(media_server: MediaServer):
    playback_command(media_server, "StopAll")


def playback_previous(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, "Previous", zone)


def playback_next(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, "Next", zone)


def playback_command(media_server: MediaServer, command: str, zone: Zone = Zone()):
    """Issues a playback command to the server.

    Sends a playback command to the given server. Available commands are:
    Play, PlayPause, Pause, Stop, StopAll, Next, Previous.
    Optionally, provide a zone as target for the playback, otherwise the
    zone currently selected in the MC GUI is targeted.
    """

    payload = {"Zone": zone.best_identifier(), "ZoneType": zone.best_identifier_type()}
    extension = "Playback/" + command
    media_server.send_request(extension, payload)


def playback_zones(media_server: MediaServer, see_hidden: bool = False):
    """Returns a list of zones available at the given server.

    see_hidden: If true, zones that were hidden by a user are returned as well.
    """

    see_hidden = "1" if see_hidden else "0"
    payload = {"Hidden": see_hidden}
    response = media_server.send_request("Playback/Zones", payload)
    response.raise_for_status()
    content = transform_unstructured_response(response)
    num_zones = int(content["NumberZones"])
    # The zones are returned a bit unintuitively,
    # requiring this loop to reconstruct them
    zones = []
    for i in range(num_zones):
        zone = Zone()
        zone.index = i
        zone.id = content["ZoneID" + str(i)]
        zone.name = content["ZoneName" + str(i)]
        zone.guid = content["ZoneGUID" + str(i)]
        zone.is_dlna = True if (content["ZoneDLNA" + str(i)] == "1") else False
        zones.append(zone)
    return zones


def playback_position(
    media_server: MediaServer,
    position: int = None,
    relative: int = None,
    zone: Zone = Zone(),
) -> int:
    """Get or set the playback position.

    position: The position to seek to in milliseconds. If left as None,
              position is returned only. Set to -1 to choose default jump length based on media type.
    relative: When set to 1, 'Position' will be added to the current position to allow jumping forward.
              When set to -1, 'Position' will be subtracted from the current position to allow jumping
              backwards. Use a 'Position' of -1 to jump the default amount based on the media type.
    zone:     Target zone for the command.
    returns: The playback position (after changes, if applicable).
    """
    payload = {"Position": position, "Relative": relative}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/Position", payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return int(response["Position"])


def playback_volume(
    media_server: MediaServer,
    level: float = None,
    relative: bool = False,
    zone: Zone = Zone(),
) -> float:
    """Get or set the playback volume.

    level:    The level as a value between 0 and 1. If left to None, volume is
              returned unchanged.
    relative: If set to False or None, volume will be set to this value.
              if set to True, value will be adjusted by this value.
    zone:     Target zone for the command.
    returns:  Diverging from MCWS, this method only returns the float volume
              after changes have been applied (no additional display string).
    """
    relative = "1" if relative else "0"
    payload = {"Level": level, "Relative": relative}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/Volume", payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return float(response["Level"])


def playback_mute(
    media_server: MediaServer, set: bool = None, zone: Zone = Zone()
) -> bool:
    """Get or set the mute mode.

    set:     The boolean value representing the new mute state. Leave to None
             to return state only.
    zone:    Target zone for the command.
    returns: The mute state after changes took effect.
    """
    if set is None:
        set = ""
    else:
        set = "1" if set else "0"
    payload = {"Set": set}
    response = media_server.send_request("Playback/Mute", payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return response["State"] == "1"


def playback_repeat(
    media_server: MediaServer, mode: str = None, zone: Zone = Zone()
) -> str:
    """Get or set the repeat mode.

    mode:    The repeat mode, a string of either: Off, Playlist, Track, Stop, Toggle,
             or None to retrieve repeat value
    zone:    Target zone for the command.
    returns: The shuffle state after changes took effect.
    """
    payload = {"Mode": mode}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/Repeat", payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return response["Mode"]


def playback_shuffle(
    media_server: MediaServer, mode: str = None, zone: Zone = Zone()
) -> str:
    """Get or set the shuffle state.

    mode:    The suffle mode, a string of either: Off, On, Automatic, Toogle, Reshuffle
    zone:    Target zone for the command.
    returns: The shuffle state after changes took effect.
    """
    payload = {"Mode": mode}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/Shuffle", payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return response["Mode"]


#
#   FILE
#


def file_get_image(
    media_server: MediaServer,
    file,
    type: str = "Thumbnail",
    thumbnail_size: str = None,
    width: int = None,
    height: int = None,
    fill_transparency: str = None,
    square: bool = False,
    pad: bool = False,
    format: str = "jpg",
    transform_to_pil: bool = True,
) -> Image:
    """Returns an image for the given library file.

    file:   A dictionary of tags, as returned by files_search()
    type:   The type of image to get: Thumbnail (default), Full, ThumbnailsBinary
    thumbnail_size: The size of the thumbnail (if type is thumbnail): Small, Medium, Large
    width:  The width for the returned image.
    height: The height for the returned image.
    fill_transparency: A color to fill image transparency with (hex number).
    square: Set to 1 to crop the image to a square aspect ratio.
    pad:    Set to 1 to pad around the image with transparency to fulfil the requested size.
    format: The preferred image format (jpg or png).
    returns: A pillow image if transform_to_pil is True, and a response object otherwise.
    """
    pad = "1" if pad else "0"
    square = "1" if square else "0"
    payload = {
        "Type": type,
        "ThumbnailSize": thumbnail_size,
        "Width": width,
        "Height": height,
        "FillTransparency": fill_transparency,
        "Square": square,
        "Pad": pad,
        "Format": format,
    }
    if file.get("Key", None) is not None:
        payload["File"] = file["Key"]
        payload["FileType"] = "Key"
    else:
        payload["File"] = file["Filename"]
        payload["FileType"] = "Filename"
    response = media_server.send_request("File/GetImage", payload)
    # Error 500 indicates that no cover was present
    if response.status_code == 500:
        return None
    response.raise_for_status()
    if transform_to_pil:
        return Image.open(BytesIO(response.content))
    else:
        return response


#
#   FILES
#


def files_search(
    media_server: MediaServer,
    query: str,
    action: str,
    fields=None,
    use_play_doctor: bool = False,
    shuffle: bool = False,
    no_local_filenames=False,
    zone=None,
):
    payload = {"Action": action, "Query": query}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    payload["NoLocalFilenames"] = "1" if no_local_filenames else "0"
    payload["PlayDoctor"] = "1" if use_play_doctor else "0"
    payload["Shuffle"] = "1" if shuffle else "0"
    if fields is not None:
        fields = ",".join(fields)
        payload["Fields"] = fields
    response = media_server.send_request("Files/Search", payload)
    if action != "MPL":
        return response
    else:
        return transform_mpl_response(media_server, response)


#
#   Library
#


def library_values(
    media_server: MediaServer,
    filter: str = None,
    field: str = None,
    files: str = None,
    limit: str = None,
):
    payload = {"Filter": filter, "Field": field, "Files": files, "Limit": limit}
    response = media_server.send_request("Library/Values", payload)
    response.raise_for_status()
    return transform_list_response(response)


#
#   HELPER
#


def transform_unstructured_response(response):
    """Converts the relatively unstructured XML responses from MCWS into
    a dictionary that is easier to process.
    """
    result = {}
    root = ElementTree.fromstring(response.content)
    for child in root:
        result[child.attrib["Name"]] = child.text
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
        result.append(tags)
    return result


def get_media_server(access_key: str, username: str, password: str) -> MediaServer:
    """Returns an instance of media server with the given parameters.

    This is mainly syntactical sugar for people that only want to import pymcws
    and be done with it.
    """
    return MediaServer(access_key, username, password)


def escape_for_query(query_part: str) -> str:
    """Escapes all characters reserved by jriver in a natural string.

    Do not put a complete query in here - this method is used to escape
    reserved characters in a natural string that will be used as a query fragment.
    This is usually the content of a field (e.g. an album or artist name).
    """
    query_part = query_part.replace('"', '/"')  # replace " with /"
    query_part = query_part.replace("^", "/^")
    query_part = query_part.replace("[", "/[")
    query_part = query_part.replace("]", "/]")
    return query_part
