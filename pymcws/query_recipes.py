from .media_server import MediaServer, Zone
from .api import files_search, escape_for_query


def query_album(media_server: MediaServer, album_artist: str, album: str):
    """Plays an Album by a given Album Artist.
    """
    album_artist = escape_for_query(album_artist)
    album = escape_for_query(album)
    query = '[Album Artist]=[' + album_artist + '] [Album]=[' + album + '] ~sort=[Disc #],[Track #]'
    response = files_search(media_server, query, 'MPL')
    return response
