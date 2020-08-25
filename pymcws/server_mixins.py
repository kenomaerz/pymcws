""" This file contains householding classes that enable the direct import of API functions
    into the MediaServer class. Implementing a new function in the API should usually
    be followed by adding this function here.
"""


class MediaServerDummy:
    def __init__(self, server):
        self.__server = server
        self.send_request = self.__server.send_request
        self.fields = self.__server.fields


class File(MediaServerDummy):
    from pymcws.api.file import set_info


class Files(MediaServerDummy):
    from pymcws.api.files import get_image, search, transform_mpl_response


class Library(MediaServerDummy):
    from pymcws.api.library import (
        create_file,
        get_default,
        get_list,
        fields,
        get_loaded,
    )


class Playback(MediaServerDummy):
    from pymcws.api.playback import (
        command,
        loadDSPreset,
        mute,
        next,
        pause,
        play,
        playpause,
        position,
        previous,
        repeat,
        shuffle,
        stop,
        stopall,
        volume,
        info,
        set_playlist,
        zones,
    )


class Recipes(MediaServerDummy):
    from pymcws.api.recipes import (
        play_album,
        play_keyword,
        query_album,
        query_keyword,
    )
