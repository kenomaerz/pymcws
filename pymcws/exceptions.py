class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class UnresolvableKeyError(Error):
    """Exception raised if access key is unresolvable.

    Attributes:
        key -- The key that could not be resolved
        message -- message as given by jriver web service
    """

    def __init__(self, key, message):
        self.key = key
        self.message = message
