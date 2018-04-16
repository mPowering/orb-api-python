"""
ORB API specific exceptions
"""


class OrbApiException(Exception):
    def __init__(self, message, error_code):
        super(OrbApiException, self).__init__(str(error_code) + ": " + message)


class OrbRequestLimit(Exception):
    def __init__(self):
        super(OrbRequestLimit, self).__init__(429, "Request limit reached")


class OrbApiResourceExists(OrbApiException):
    def __init__(self, message, error_code, pk):
        super(OrbApiResourceExists, self).__init__(str(error_code) + ": " + message)
        self.pk = pk
        self.code = error_code
        self.message = message
