"""
Data modelling classes
"""


class OrbResource(object):
    def __init__(
            self, id=None, title=None, description=None, study_time_number=0, study_time_unit=None, attribution=None):
        self.id = id
        self.title = title
        self.description = description
        self.study_time_number = study_time_number
        self.study_time_unit = study_time_unit
        self.attribution = attribution


class OrbResourceFile(object):
    def __init__(self, file='', title='', description='', order_by=0):
        self.file = file
        self.title = title
        self.description = description
        self.order_by = order_by


class OrbResourceURL(object):
    def __init__(self, url='', title='', description='', order_by=0, file_size=0):
        self.url = url
        self.title = title
        self.description = description
        self.order_by = order_by
        self.file_size = file_size
