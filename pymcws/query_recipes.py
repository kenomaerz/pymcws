from .media_server import MediaServer, Zone
from .api import files_search


def query_album(media_server: MediaServer, album_artist: str, album: str):
    """Plays an Album by a given Album Artist.
    """
    query = '[Album Artist]=[' + album_artist + '] [Album]=[' + album + ']'
    response = files_search(media_server, query, 'MPL')
    return response
