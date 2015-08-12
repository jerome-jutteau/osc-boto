# -*- coding:utf-8 -*-
"""
Object model for snapshot export tasks
"""
from boto.ec2.ec2object import EC2Object


class SnapshotExportTask(EC2Object):
    def __init__(self, connection=None):
        """
        Represents a Snapshot export task.

        :ivar id: The unique ID of the export task.
        :ivar snapshot_id: ID of the snashot being exported
        :ivar state: The current state of the export (active|completed|failed).
        :ivar status: Status message in case of error.
        :ivar disk_image_format: Format of the exported snapshot.
        :ivar bucket: Name of the target bucket.
        :ivar key: Target key in the bucket.
        """
        super(SnapshotExportTask, self).__init__(connection)
        self.id = None
        self.snapshot_id = None
        self.state = None
        self.status_message = None
        self.disk_image_format = None
        self.bucket = None
        self.key = None
        self.access_key = None
        self.secret_key = None

    def __repr__(self):
        return 'SnapshotExportTask:%s' % self.id

    def endElement(self, name, value, connection):
        if name == 'snapshotExportTaskId':
            self.id = value
        elif name == 'state':
            self.state = value
        elif name == 'statusMessage':
            self.status_message = value
        elif name == 'snapshotId':
            self.snapshot_id = value
        elif name == 'diskImageFormat':
            self.disk_image_format = value
        elif name == 'osuBucket':
            self.bucket = value
        elif name == 'osuKey':
            self.key = value
        elif name == 'AccessKey':
            self.access_key = value
        elif name == 'SecretKey':
            self.secret_key = value
        elif name in ['snapshotExport', 'snapshotExportTask', 'exportToOsu', 'aksk']:
            pass
        else:
            setattr(self, name, value)

    def update(self):
        pass
