from .media_server import MediaServer


class File(dict):
    """ A class behaving like a dict that abstracts a file object on a madia server.

        This class keeps track of changes made to the metadata, enabling smart saving
        of changed values. Changing data in this object has no effect on the server until
        File.save_changes(...) is called. Creation of files is typically managed by the
        MediaServer or the API. New files should be created using api.library_create_file(...).
        Deleting keys from a file does NOT change data on the server, instead the respective
        tag will be ignored in future iterations until added again.
    """

    def __init__(self, server: MediaServer, initial_fields):
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
    """ Helper method that translates Windows and Unix filepaths
    """
    for file in files:
        file = file.replace(search_for, replace_with)
        if win_to_unix:
            file = file.replace("\\", "/")
        elif unix_to_win:
            file = file.replace("/", "\\")
    return files
