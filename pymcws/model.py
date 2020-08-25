import logging

logger = logging.getLogger(__name__)


class Zone:
    """Zones represent targets for playback-related commands.

    Zones are available on a per-server basis and can be retrieved for each
    using MCWS. If you know the id or name of the zone that you want to target,
    you can also create a zone and set id, index or name manually. The missing
    fields do not affect functionality, the best available value is retrieved
    automatically.
    """

    def __init__(self):
        self.id = -1  # Default ID indicating the zone currently selected in MC
        self.index = None
        self.name = None
        self.guid = None
        self.is_dlna = None

    def best_identifier(self):
        """Checks available fields and retirves the best available.

        Use best_identifier_type() to find out what type of identifier was
        returned.
        """
        if self.id is not None:
            return self.id
        if self.name is not None:
            return self.name
        if self.index is not None:
            return self.index
        logger.warn(
            "Unable to determine best identifier "
            + " for Zone. This is probably a bug."
        )

    def best_identifier_type(self):
        """ Returns the type of the best identifier.

        Used in conjunction with best_identifier() to automatically determine
        the best strategy to communicate zones to the MCWS API.
        """
        if self.id is not None:
            return "ID"
        if self.name is not None:
            return "Name"
        if self.index is not None:
            return "Index"
        logger.warn(
            "Unable to determine best identifier type"
            + " for Zone. This is probably a bug."
        )

    def __str__(self):
        return self.name


class MediaFile(dict):
    """ A class behaving like a dict that represents a file object on a media server.

        It does NOT represent a physical file!
        This class keeps track of changes made to the metadata, enabling smart saving
        of changed values. Changing data in this object has no effect on the server until
        File.save_changes(...) is called. Creation of files is typically managed by the
        MediaServer or the API. New files should be created using api.library_create_file(...).
        Deleting keys from a file does NOT change data on the server, instead the respective
        tag will be ignored in future iterations until added again.
    """

    def __init__(self, server, initial_fields):
        """ Creates a new File object representing a file on the server. Do not call in your code!

            File creation needs to happen on the server. If you need a new file,
            call api.library_create_file()
        """
        dict.__init__(self)
        self.__server = server
        self.update(initial_fields)
        self.__changed = {}
        for key in initial_fields:
            self.__changed[key] = False

    def __setitem__(self, key, val):
        if val != self.get(key, None):
            dict.__setitem__(self, key, val)
            self.__changed[key] = True

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        del self.__changed[key]

    @property
    def changed_fields(self) -> dict:
        return dict(
            filter(lambda elem: self.__changed[elem[0]] is not False, self.items())
        )


def transform_path(
    files,
    search_for: str,
    replace_with: str,
    win_to_unix: bool = False,
    unix_to_win: bool = False,
):
    """ Helper method that translates Windows and Unix filepaths in JRFiles
    """
    for file in files:
        file = file.replace(search_for, replace_with)
        if win_to_unix:
            file = file.replace("\\", "/")
        elif unix_to_win:
            file = file.replace("/", "\\")
    return files
