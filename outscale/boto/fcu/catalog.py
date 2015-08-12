# -*- coding:utf-8 -*-
"""
Object model for catalogs
"""

from boto.ec2.ec2object import EC2Object, TagSet
from boto.resultset import ResultSet


class TokenList(list):
    def __init__(self):
        super(TokenList, self).__init__()
        self.markers = []

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 'item':
            self.append(value)


class Value(EC2Object):
    def __init__(self, connection=None):
        super(Value, self).__init__(connection)
        self.value = None
        self.tokens = TokenList()

    def startElement(self, name, attrs, connection):
        if name == 'tokenSet':
            return self.tokens
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'value':
            self.value = value
        else:
            setattr(self, name, value)


class Entry(EC2Object):
    def __init__(self, connection=None):
        super(Entry, self).__init__(connection)
        self.attributes = TagSet()
        self.key = None
        self.values = ResultSet([('item', Value)])

    def startElement(self, name, attrs, connection):
        if name == 'attributeSet':
            return self.attributes
        elif name == 'valueSet':
            return self.values
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'key':
            self.key = value
        else:
            setattr(self, name, value)


class Catalog(EC2Object):
    def __init__(self, connection=None):
        """
        Represents a Snapshot export task.

        :ivar entries: catalog entries
        :ivar attributes: catalog attributes
        """
        super(Catalog, self).__init__(connection)
        self.entries = ResultSet([('item', Entry)])
        self.attributes = TagSet()

    def __repr__(self):
        return 'Catalog'

    def startElement(self, name, attrs, connection):
        if name == 'attributeSet':
            return self.attributes
        elif name == 'entrySet':
            return self.entries
        else:
            return None

    def endElement(self, name, value, connection):
        pass

    def update(self):
        pass
