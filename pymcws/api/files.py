from io import BytesIO
from pymcws.utils import transform_mpl_response
from pymcws.model import MediaFile, Zone


def get_image(
    media_server,
    file: MediaFile,
    type: str = "Thumbnail",
    thumbnail_size: str = None,
    width: int = None,
    height: int = None,
    fill_transparency: str = None,
    square: bool = False,
    pad: bool = False,
    format: str = "jpg",
    return_url: bool = False,
):
    """Returns an image (or image url) for the given library file.

    MCWS provides cover art for all files at the get_image endpoint and will process the image
    according to your specifications. You can use this method to either format a url for or to
    download the image and return it as a byte array. When returning URLs, be aware that the URL
    will contain information relevant to the media server, possibly a username and password.
    When requesting an image, pymcws will return an array of bytes that can then be read by your
    favorite library, e.g. in pillow: Image.open(BytesIO(returned_bytes))).

    file:       A dictionary of tags, as returned by files_search().
    type:       The type of image to get: Thumbnail (default), Full, ThumbnailsBinary.
    thumbnail_size: The size of the thumbnail (if type is thumbnail): Small, Medium, Large.
    width:      The width for the returned image.
    height:     The height for the returned image.
    fill_transparency: A color to fill image transparency with (hex number).
    square:     Set to 1 to crop the image to a square aspect ratio.
    pad:        Set to 1 to pad around the image with transparency to fulfil the requested size.
    format:     The preferred image format (jpg or png).
    return_url: Return an image url instead of the image; Cave: The URL contains
                information relevant to the server.
    returns:    An array of bytes representing the image (PIL: Image.open(BytesIO(returned))) if
                return_url is False, and a URL to the image otherwise.
    """
    pad = "1" if pad else "0"
    square = "1" if square else "0"
    payload = {
        "Type": type,
        "ThumbnailSize": thumbnail_size,
        "Width": width,
        "Height": height,
        "FillTransparency": fill_transparency,
        "Square": square,
        "Pad": pad,
        "Format": format,
    }
    if file.get("Key", None) is not None:
        payload["File"] = file["Key"]
        payload["FileType"] = "Key"
    else:
        payload["File"] = file["Filename"]
        payload["FileType"] = "Filename"
    if return_url:
        return
    response = media_server.send_request("File/GetImage", payload)
    # Error 500 indicates that no cover was present
    if response.status_code == 500:
        return None
    response.raise_for_status()
    return response.content


def search(
    media_server,
    query: str,
    action: str = "MPL",
    fields: list[str] = None,
    play_doctor: bool = False,
    shuffle: bool = False,
    no_local_filenames=False,
    zone: Zone = None,
):
    payload = {"Action": action, "Query": query}
    if zone is not None:
        payload["Zone"] = zone.best_identifier()
        payload["ZoneType"] = zone.best_identifier_type()
    payload["NoLocalFilenames"] = "1" if no_local_filenames else "0"
    payload["PlayDoctor"] = "1" if play_doctor else "0"
    payload["Shuffle"] = "1" if shuffle else "0"
    if fields is not None:
        fields = ",".join(fields)
        payload["Fields"] = fields
    response = media_server.send_request("Files/Search", payload)
    if action != "MPL":
        return response
    else:
        return transform_mpl_response(media_server, response)
