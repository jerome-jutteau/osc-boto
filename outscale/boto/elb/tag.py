# -*- coding:utf-8 -*-
"""
Module to manage ELB tags in boto.
"""

class Tag(object):
    """
    Represents an ELB Tag.
    """

    def __init__(self, connection=None, endpoints=None):
        """
        """
        self.connection = connection
        self.name = None
        self.value = None

    def __repr__(self):
        return 'Tag:%s:%s' % (self.name, self.value)

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Key':
            self.name = value
        elif name == 'Value':
            self.value = value
        else:
            setattr(self, name, value)
