from .media_server import MediaServer, Zone
from .api import files_search


def play_album(media_server: MediaServer, album_artist: str, album: str,
               use_play_doctor: bool = False, zone: Zone = None):
    """Plays an Album by a given Album Artist.
    """
    query = '[Album Artist]=[' + album_artist + '] [Album]=[' + album + '] ~sort=[Disc #],[Track #]'
    response = files_search(media_server, query, 'play', use_play_doctor)
    response.raise_for_status()


def play_keyword(media_server: MediaServer, keyword: str, use_play_doctor: bool = False,
                 shuffle: bool = True, zone: Zone = None):
    """Plays songs given by a specific keyword.
    """
    query = '[keywords]=[' + keyword + ']'
    response = files_search(media_server, query, 'play', use_play_doctor, shuffle)
    response.raise_for_status()
