# -*- coding:utf-8 -*-
"""
Object model for product types
"""
from boto.ec2.ec2object import EC2Object


class InstanceType(EC2Object):
    def __init__(self, connection=None):
        """
        Represents an instance type

        :ivar name: ID of the type
        :ivar vpcu: vCPU for this instance type
        :ivar memory: amount of memory in bytes
        :ivar storage_size: size of ephemeral disks in bytes (optional)
        :ivar storage_count: maximum number of ephemeral disks
        :ivar max_ip_addresses: maximum number of private ip addresses per NIC
        :ivar ebs_optimized_available: whether EBS optimized option is available for this instance type
        """
        super(InstanceType, self).__init__(connection)
        self.name = None
        self.vcpu = None
        self.memory = None
        self.storage_size = None
        self.storage_count = None
        self.max_ip_addresses = None
        self.ebs_optimized_available = None

    def __repr__(self):
        return 'InstanceType:%s' % self.name

    def endElement(self, name, value, connection):
        if name == 'name':
            self.name = value
        elif name == 'vcpu':
            self.vcpu = int(value)
        elif name == 'memory':
            self.memory = int(value)
        elif name == 'storageSize':
            self.storage_size = int(value)
        elif name == 'storageCount':
            self.storage_count = int(value)
        elif name == 'maxIpAddresses':
            self.max_ip_addresses = int(value)
        elif name == 'ebsOptimizedAvailable':
            self.ebs_optimized_available = True if value == 'true' else False
        else:
            setattr(self, name, value)
