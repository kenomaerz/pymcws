from .media_server import MediaServer, Zone
from .api import files_search, escape_for_query, playback_repeat, playback_shuffle


def play_album(
    media_server: MediaServer,
    album_artist: str,
    album: str,
    shuffle: bool = False,
    use_play_doctor: bool = False,
    repeat: bool = None,
    zone: Zone = None,
):
    """ Plays an Album by a given Album Artist.
    
        By default, this call disables shuffle, so the album can be listened in the intended order.
        set shuffle to None to avoid this and preserve shuffle state.
        Setting shuffle to True only shuffles order of files and leaves playback state alone
    """
    album_artist = escape_for_query(album_artist)
    album = escape_for_query(album)
    if shuffle is False:
        playback_shuffle(media_server, mode="Off")
    query = (
        "[Album Artist]=["
        + album_artist
        + "] [Album]=["
        + album
        + "] ~sort=[Disc #],[Track #]"
    )
    response = files_search(
        media_server, query, "play", shuffle=shuffle, use_play_doctor=use_play_doctor
    )
    response.raise_for_status()
    if repeat is not None:
        repeat = "Playlist" if repeat else "Off"
        response = playback_repeat(media_server, mode=repeat, zone=zone)


def play_keyword(
    media_server: MediaServer,
    keyword: str,
    use_play_doctor: bool = False,
    shuffle: bool = True,
    zone: Zone = None,
):
    """ Plays songs given by a specific keyword.
    """
    keyword = escape_for_query(keyword)
    query = "[keywords]=[" + keyword + "]"
    response = files_search(
        media_server, query, "play", use_play_doctor=use_play_doctor, shuffle=shuffle
    )
    response.raise_for_status()
