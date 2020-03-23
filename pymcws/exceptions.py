class PymcwsError(Exception):
    """Base class for exceptions in this module."""

    pass


class UnresolvableKeyError(PymcwsError):
    """Exception raised if access key is unresolvable.

    More specifically, JRiver web services were available, but do not know the given key.

    Attributes:
        key -- The key that could not be resolved
        message -- message as given by jriver web service
    """

    def __init__(self, key, message):
        self.key = key
        self.message = message
