from pymcws.model import Zone
from pymcws.api.files import search
from pymcws.utils import escape_for_query
from typing import List, Dict
from pymcws.api.playback import shuffle, repeat


def play_album(
    media_server,
    album_artist: str,
    album: str,
    shuffle_album: bool = False,
    use_play_doctor: bool = False,
    repeat_album: bool = False,
    zone: Zone = None,
):
    """ Plays an album by a given album artist.

        By default, this call disables shuffle and repeat, so the album can be listened in the intended order.
        set either to None to avoid this and preserve shuffle/repeat state.
        Setting shuffle_album to True shuffles order of files in playlist and leaves playback state alone.
        Setting shuffle to False keeps playlist in order and disables shuffle.
    """
    album_artist = escape_for_query(album_artist)
    album = escape_for_query(album)
    if shuffle_album is False:
        shuffle(media_server, mode="Off", zone=zone)
    query = (
        "[Album Artist]=["
        + album_artist
        + "] [Album]=["
        + album
        + "] ~sort=[Disc #],[Track #]"
    )
    response = search(
        media_server,
        query,
        "play",
        shuffle=shuffle_album,
        use_play_doctor=use_play_doctor,
        zone=zone,
    )
    response.raise_for_status()
    if repeat_album is not None:
        mode = "Playlist" if repeat_album else "Off"
        response = repeat(media_server, mode=mode, zone=zone)


def play_keyword(
    media_server,
    keyword: str,
    use_play_doctor: bool = False,
    shuffle_list: bool = True,
    zone: Zone = None,
):
    """ Plays songs given by a specific keyword.
    """
    keyword = escape_for_query(keyword)
    query = "[keywords]=[" + keyword + "]"
    response = search(
        media_server,
        query,
        "play",
        use_play_doctor=use_play_doctor,
        shuffle=shuffle_list,
        zone=zone,
    )
    response.raise_for_status()


def query_album(media_server, album_artist: str, album: str) -> Dict:
    """Returns files from an Album by a given Album Artist.
    """
    album_artist = escape_for_query(album_artist)
    album = escape_for_query(album)
    query = (
        "[Album Artist]=["
        + album_artist
        + "] [Album]=["
        + album
        + "] ~sort=[Disc #],[Track #]"
    )
    response = search(media_server, query, "MPL")
    return response


def query_keyword(media_server, keyword: str, sort_criteria: List[str] = None) -> Dict:
    """Returns all files tagged with a specific keyword.

    sort_criteria: a list of strings that contain fieldnames by which to sort the result
    """
    keyword = escape_for_query(keyword)
    query = "[keywords]=[" + keyword + "]"
    if sort_criteria is not None:
        query += " ~sort="
        for criterion in sort_criteria:
            query += "[" + criterion + "],"
        query = query[:-1]
    response = search(media_server, query, "MPL")
    return response
