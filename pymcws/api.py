from .media_server import MediaServer, Zone
# import logging
from xml.etree import ElementTree


def alive(media_server: MediaServer):
    response = media_server.send_request("Alive")
    return (transform_unstructured_response(response))

#
#   PLAYBACK
#


def playback_play(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, 'Play', zone)


def playback_playpause(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, 'PlayPause', zone)


def playback_stop(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, 'Stop', zone)


def playback_stopall(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, 'StopAll', zone)


def playback_previous(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, 'Previous', zone)


def playback_next(media_server: MediaServer, zone: Zone = Zone()):
    playback_command(media_server, 'Next', zone)


def playback_command(media_server: MediaServer, command: str, zone: Zone = Zone()):
    """Issues a playback command to the server.

    Sends a playback command to the given server. Available commands are:
    Play, PlayPause, Pause, Stop, StopAll, Next, Previous.
    Optionally, provide a zone as target for the playback, otherwise the
    zone currently selected in the MC GUI is targeted.
    """

    payload = {'Zone': zone.best_identifier(), 'ZoneType': zone.best_identifier_type()}
    extension = "Playback/" + command
    media_server.send_request(extension, payload)


def playback_zones(media_server: MediaServer, see_hidden: bool = False):
    """Returns a list of zones available at the given server.

    see_hidden: If true, Zones that were hidden by a user are returned as well.
    """

    see_hidden = '1' if see_hidden else '0'
    payload = {'Hidden': see_hidden}
    response = media_server.send_request('Playback/Zones', payload)
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
        zone.is_dlna = True if (content["ZoneDLNA" + str(i)] == '1') else False
        zones.append(zone)
    return zones


def playback_position(media_server: MediaServer, position: int = None,
                      relative: bool = False, zone: Zone = Zone()) -> int:
    """Get or set the playback position.

    position: The position to seek to in milliseconds. If left to none,
              position is returned only.
    relative: If set to False or None, playback will jumo to absolute position.
              If set to True, Position argument will be added or subtracte from
              current position (seeking).
    zone:     Target zone for the command.
    Returns: The playback position after changes.
    """
    relative = '1' if relative else '0'
    payload = {'Position': position, 'Relative': relative, 'Zone': zone.best_identifier(),
               'ZoneType': zone.best_identifier_type()}
    response = media_server.send_request('Playback/Position', payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return int(response["Position"])


def playback_volume(media_server: MediaServer, level: float = None,
                    relative: bool = False, zone: Zone = Zone()) -> float:
    """Get or set the playback volume.

    level:    The level as a value between 0 and 1. If left to None, vilume is
              returned only.
    relative: If set to False or None, volume will be set to this value.
              if set to True, value will be adjusted by this value.
    zone:     Target zone for the command.
    returns:  Diverging from MCWS, this method only returns the float volume
              after changes have been applied (no additional display string).
    """
    relative = '1' if relative else '0'
    payload = {'Level': level, 'Relative': relative, 'Zone': zone.best_identifier(),
               'ZoneType': zone.best_identifier_type()}
    response = media_server.send_request('Playback/Volume', payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return float(response["Level"])


def playback_mute(media_server: MediaServer, set: bool = None,
                  zone: Zone = Zone()) -> bool:
    """Get or set the mute state.

    set:     The boolean value representng the new mute state. Leave to None
             to return state only.
    zone:    Target zone for the command.
    returns: The mute state after changes took effect.
    """
    if set is None:
        set = ""
    else:
        set = '1' if set else '0'
    payload = {'Set': set,  'Zone': zone.best_identifier(),
               'ZoneType': zone.best_identifier_type()}
    response = media_server.send_request('Playback/Mute', payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return response["State"] == '1'


def playback_shuffle(media_server: MediaServer, mode: str = None,
                     zone: Zone = Zone()) -> str:
    """Get or set the shuffle state.

    mode:    The suffle mode, a string of either: Off, On, Automatic, Toogle, Reshuffle
    zone:    Target zone for the command.
    returns: The shuffle state after changes took effect.
    """
    payload = {'Mode': mode,  'Zone': zone.best_identifier(),
               'ZoneType': zone.best_identifier_type()}
    response = media_server.send_request('Playback/Shuffle', payload)
    response.raise_for_status()
    response = transform_unstructured_response(response)
    return response["Mode"]

#
#   FILES
#


def files_search(media_server: MediaServer, query: str, action: str,
                 use_play_doctor: bool = False, shuffle: bool = False):
    payload = {'Action': action, 'Query': query}
    payload["playDoctor"] = '1' if use_play_doctor else '0'
    payload["Shuffle"] = '1' if shuffle else '0'

    response = media_server.send_request("Files/Search", payload)
    return response

#
#   HELPER
#


def transform_unstructured_response(response):
    """Converts the relatively unstructured xml responses from mcws into
    a ditcionary that easier to process.
    """
    result = {}
    root = ElementTree.fromstring(response.content)
    for child in root:
        result[child.attrib["Name"]] = child.text
    return result


def get_media_server(access_key: str, username: str, password: str) -> MediaServer:
    """Returns an instance of media server with the given parameters.

    This is mainly syntactical sugar for eople that only want to import pymcws
    and be done with it.
    """
    return MediaServer(access_key, username, password)
