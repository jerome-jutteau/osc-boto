# -*- coding:utf-8 -*-
"""
Object model for product types
"""
from boto.ec2.ec2object import EC2Object


class ProductType(EC2Object):
    def __init__(self, connection=None):
        """
        Represents a product type

        :ivar id: ID of the type
        :ivar description: description of the type
        """
        super(ProductType, self).__init__(connection)
        self.id = None
        self.description = None

    def __repr__(self):
        return 'ProductType:%s' % self.id

    def endElement(self, name, value, connection):
        if name == 'productTypeId':
            self.id = value
        elif name == 'description':
            self.description = value
        else:
            setattr(self, name, value)
