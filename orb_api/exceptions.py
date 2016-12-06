"""
ORB API specific exceptions
"""


class OrbApiException(Exception):
    def __init__(self, message, error_code):
        super(OrbApiException, self).__init__(str(error_code) + ": " + message)


class OrbApiResourceExists(OrbApiException):
    def __init__(self, message, error_code, pk):
        super(OrbApiResourceExists, self).__init__(str(error_code) + ": " + message)
        self.pk = pk
        self.code = error_code
        self.message = message
