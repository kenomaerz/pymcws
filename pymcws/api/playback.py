from pymcws.model import Zone
from pymcws.utils import transform_unstructured_response, serialize_file_list
import logging

logger = logging.getLogger(__name__)


def play(media_server, zone: Zone = Zone()):
    command(media_server, "Play", zone)


def pause(media_server, zone: Zone = Zone()):
    command(media_server, "Pause", zone)


def playpause(media_server, zone: Zone = Zone()):
    command(media_server, "PlayPause", zone)


def stop(media_server, zone: Zone = Zone()):
    command(media_server, "Stop", zone)


def stopall(media_server):
    command(media_server, "StopAll")


def previous(media_server, zone: Zone = Zone()):
    command(media_server, "Previous", zone)


def next(media_server, zone: Zone = Zone()):
    command(media_server, "Next", zone)


def command(media_server, command: str, zone: Zone = Zone()):
    """Issues a playback command to the server.

    Sends a playback command to the given server. Available commands are:
    Play, PlayPause, Pause, Stop, StopAll, Next, Previous.
    Optionally, provide a zone as target for the playback, otherwise the
    zone currently selected in the MC GUI is targeted.
    """

    payload = {"Zone": zone.best_identifier(), "ZoneType": zone.best_identifier_type()}
    extension = "Playback/" + command
    media_server.send_request(extension, payload)


def zones(media_server, see_hidden: bool = False):
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


def position(
    media_server, position: int = None, relative: int = None, zone: Zone = Zone(),
) -> int:
    """Get or set the playback position.

    position: The position to seek to in milliseconds. If left as None,
              position is returned only. Set to -1 to choose default jump length based on media type.
    relative: When set to 1, 'Position' will be added to the current position to allow jumping forward.
              When set to -1, 'Position' will be subtracted from the current position to allow jumping
              backwards. Use a 'Position' of -1 to jump the default amount based on the media type.
    zone:     Target zone for the command.
    returns:  The playback position (after changes, if applicable).
    """
    payload = {"Position": position, "Relative": relative}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/Position", payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return int(response["Position"])


def volume(
    media_server,
    level: float = None,
    relative: bool = False,
    zone: Zone = Zone(),
    return_display_string: bool = False,
) -> float:
    """Get or set the playback volume.

    level:    The level as a value between 0 and 1. If left to None, volume is
              returned unchanged.
    relative: If set to False or None, volume will be set to this value.
              if set to True, value will be adjusted by this value.
    zone:     Target zone for the command.
    return_display_string: If set to true, this method returns a human readable
              string instead of a float value. Set to "both" to return a tuple.
    returns:  returns the float volume if return_display_string is False,
              and a human readable string otherwise.
    """
    relative = "1" if relative else "0"
    payload = {"Level": level, "Relative": relative}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/Volume", payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)

    if return_display_string:
        return response["Display"]
    else:
        return float(response["Level"])


def mute(media_server, mode: bool = None, zone: Zone = Zone()) -> bool:
    """Get or set the mute state. Contrary to mcws, calling this with default params
       will return the mute state without changes instead of setting it to False.

    mode:    The boolean value representing the new mute state. Leave to None
             to return state only.
    zone:    Target zone for the command.
    returns: The mute state after changes took effect.
    """
    if mode is None:
        return info(media_server)["VolumeDisplay"] == "Muted"

    mode = "1" if mode else "0"
    payload = {"Set": mode}
    response = media_server.send_request("Playback/Mute", payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return response["State"] == "1"


def repeat(media_server, mode: str = None, zone: Zone = Zone()) -> str:
    """Get or set the repeat mode.

    mode:    The repeat mode, a string of either: Off, Playlist, Track, Stop, Toggle,
             or None to retrieve repeat value. The value False is interpreted as 'off'.
    zone:    Target zone for the command.
    returns: The repeat state after changes took effect.
    """
    if mode == False:
        mode = "Off"
    payload = {"Mode": mode}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/Repeat", payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return response["Mode"]


def shuffle(media_server, mode: str = None, zone: Zone = Zone()) -> str:
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


def info(media_server, zone: Zone = Zone()):
    """ Returns general information on playback at the given zone.
    zone:    Target zone for the command.
    returns: A dictionary with information on the playback state.
    """
    payload = {}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/Info", payload)
    response.raise_for_status()
    return transform_unstructured_response(response, try_int_cast=True)


def set_playlist(
    media_server, files: list, zone: Zone = Zone(), active_item_index: int = -1
):
    """ Sets the given files as the playlist for the given zone.
    """
    # fix param if someone passes a single file
    if isinstance(files, dict):
        files = [files]

    playlist = None

    if isinstance(files, list):  # serialize keys, if we have a file list
        playlist = serialize_file_list(files, active_item_index)
    elif isinstance(files, str):  # if string, assume user-serialized playlist
        playlist = files
    else:
        logger.warning(
            "Could not serialize value of 'files' in playback.set_playlist(). Ignoring."
        )
    payload = {"Playlist": playlist}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/SetPlayList", payload)
    response.raise_for_status()
    return


def loadDSPreset(media_server, name: str, zone: Zone = Zone()):
    """ Loads a named DSP preset for the given zone

    name:   Name of the preset to load
    zone:   Target zone (optional)
    """
    payload = {"Name": name}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    response = media_server.send_request("Playback/LoadDSPPreset", payload)
    response.raise_for_status()
    return
