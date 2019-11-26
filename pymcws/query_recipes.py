from .media_server import MediaServer, Zone
from .api import files_search, escape_for_query
from typing import List, Dict


def query_album(media_server: MediaServer, album_artist: str, album: str) -> Dict:
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
    response = files_search(media_server, query, "MPL")
    return response


def query_keyword(
    media_server: MediaServer, keyword: str, sort_criteria: List[str] = None
) -> Dict:
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
    response = files_search(media_server, query, "MPL")
    return response
