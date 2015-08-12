# -*- coding:utf-8 -*-
"""
Represents a connection to Outscale FCU API
"""
from functools import wraps
import urlparse

import boto
from boto.ec2.connection import EC2Connection
from boto.regioninfo import get_regions


from outscale.boto.fcu.snapshot_export_task import SnapshotExportTask
from outscale.boto.fcu.catalog import Catalog
from outscale.boto.fcu.product_type import ProductType
from outscale.boto.fcu.instance_type import InstanceType


def fcuext(function):
    """
    Decorator to mark a method as part of the FCU ext API.
    Method will be called with a distinct API version
    """
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        current, self.APIVersion = self.APIVersion, self.FCUExtAPIVersion
        try:
            return function(self, *args, **kwargs)
        finally:
            self.APIVersion = current
    return wrapper


def connect_fcu_endpoint(url, aws_access_key_id, aws_secret_access_key, **kwargs):
    """
    Connect to an FCU Api endpoint.  Additional arguments are passed
    through to FCUConnection.

    :type url: string
    :param url: A url for the ec2 api endpoint to connect to

    :type aws_access_key_id: string
    :param aws_access_key_id: Your AWS Access Key ID

    :type aws_secret_access_key: string
    :param aws_secret_access_key: Your AWS Secret Access Key

    :rtype: :class:`outscale.boto.fcu.FCUConnection`
    """
    from boto.ec2.regioninfo import RegionInfo

    purl = urlparse.urlparse(url)
    kwargs['port'] = purl.port
    kwargs['host'] = purl.hostname
    kwargs['path'] = purl.path
    if not 'is_secure' in kwargs:
        kwargs['is_secure'] = (purl.scheme == "https")

    kwargs['region'] = RegionInfo(name=purl.hostname,
                                  endpoint=purl.hostname)
    kwargs['aws_access_key_id'] = aws_access_key_id
    kwargs['aws_secret_access_key'] = aws_secret_access_key

    return FCUConnection(**kwargs)


class FCUConnection(EC2Connection):

    FCUExtAPIVersion = boto.config.get('Boto', 'fcuext_version', '2015-05-07')

    @fcuext
    def export_snapshot(self, snapshot_id, bucket, disk_image_format, ak=None, sk=None, prefix=None, dry_run=False):
        """
        Export a snapshot to an OSU(S3) bucket.

        :param snapshot_id: The snapshot to export.
        :type snapshot_id: str
        :param bucket: The bucket to export to, bucket must exist and allow write access to Outscale account.
        :type bucket: str
        :param disk_image_format: The export format: vmdk vdi qcow2
        :type disk_image_format: str
        :param prefix: Prefix of the destination key in the bucket,
                       snapshot will be written to prefix + snapshot_export_task_id + '.' + disk_image_format.
        :type prefix: str
        :param ak: The access key used to create the bucket.
        :type ak: None, str
        :param sk: The secret key used to create the bucket.
        :type sk: None, str
        """
        params = {
            'SnapshotId': snapshot_id,
            'ExportToOsu.OsuBucket': bucket,
            'ExportToOsu.DiskImageFormat': disk_image_format,
        }

        if prefix is not None:
            params['ExportToOsu.OsuPrefix'] = prefix
        if ak and sk:
            params['ExportToOsu.aksk.AccessKey'] = ak
            params['ExportToOsu.aksk.SecretKey'] = sk
        if dry_run:
            params['DryRun'] = 'true'
        return self.get_object('CreateSnapshotExportTask', params, SnapshotExportTask)

    @fcuext
    def get_all_snapshot_export_tasks(self, snapshot_export_ids=None, filters=None, dry_run=False):
        params = {}
        if snapshot_export_ids:
            self.build_list_params(params, snapshot_export_ids, 'SnapshotExportTaskId')
        if filters:
            self.build_filter_params(params, dict(filters))
        if dry_run:
            params['DryRun'] = 'true'
        return self.get_list('DescribeSnapshotExportTasks', params, [('item', SnapshotExportTask)])

    @fcuext
    def get_product_type(self, snapshot_id=None, image_id=None):
        params = {
            'SnapshotId': snapshot_id,
            'ImageId': image_id
        }

        return self.get_object('GetProductType', params, ProductType)

    @fcuext
    def get_all_catalogs(self, dry_run=False):
        params = {}
        if dry_run:
            params['DryRun'] = 'true'
        return self.get_list('DescribeCatalogs', params, [('item', Catalog)])

    @fcuext
    def get_all_instance_types(self, filters=None, dry_run=False):
        params = {}

        if filters:
            self.build_filter_params(params, filters)

        if dry_run:
            params['DryRun'] = 'true'

        return self.get_list('DescribeInstanceTypes', params, [('item', InstanceType)])

    @fcuext
    def get_all_product_types(self, filters=None, dry_run=False):
        params = {}

        if filters:
            self.build_filter_params(params, filters)

        if dry_run:
            params['DryRun'] = 'true'

        return self.get_list('DescribeProductTypes', params, [('item', ProductType)])
