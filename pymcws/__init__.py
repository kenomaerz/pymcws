from pymcws.media_server import MediaServer, ApiMediaServer
from pymcws.model import Zone, MediaFile
from pymcws.api import alive
import pymcws.api.library as library
import pymcws.api.playback as playback
import pymcws.api.file as file
import pymcws.api.files as files
import pymcws.api.recipes as recipes


def get_media_server_light(
    access_key: str, username: str, password: str
) -> MediaServer:
    """Returns an instance of media server with the given parameters.

    This is mainly syntactical sugar for people that only want to import pymcws
    and be done with it.
    """
    return MediaServer(access_key, username, password)


def get_media_server(access_key: str, username: str, password: str) -> ApiMediaServer:
    """Returns an instance of media server with the given parameters.

    This is mainly syntactical sugar for people that only want to import pymcws
    and be done with it.
    """
    return ApiMediaServer(access_key, username, password)
