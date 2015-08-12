# -*- coding:utf-8 -*-

import unittest
import pytest
from outscale.boto import fcu

from mock import Mock
import httplib


# --------------------------------------------------------------------------
# cut and pasted from boto test suite

class AWSMockServiceTestCase(unittest.TestCase):
    """Base class for mocking aws services."""
    # This param is used by the unittest module to display a full
    # diff when assert*Equal methods produce an error message.
    maxDiff = None
    connection_class = None

    def setUp(self):
        self.https_connection = Mock(spec=httplib.HTTPSConnection)
        self.https_connection_factory = (
            Mock(return_value=self.https_connection), ())
        self.service_connection = self.create_service_connection(
            https_connection_factory=self.https_connection_factory,
            aws_access_key_id='aws_access_key_id',
            aws_secret_access_key='aws_secret_access_key')
        self.service_connection.get_http_connection = self.https_connection_factory[0]  # /!\ Added this line
        self.initialize_service_connection()

    def initialize_service_connection(self):
        self.actual_request = None
        self.original_mexe = self.service_connection._mexe
        self.service_connection._mexe = self._mexe_spy

    def create_service_connection(self, **kwargs):
        if self.connection_class is None:
            raise ValueError("The connection_class class attribute must be "
                             "set to a non-None value.")
        return self.connection_class(**kwargs)

    def _mexe_spy(self, request, *args, **kwargs):
        self.actual_request = request
        return self.original_mexe(request, *args, **kwargs)

    def create_response(self, status_code, reason='', header=[], body=None):
        if body is None:
            body = self.default_body()
        response = Mock(spec=httplib.HTTPResponse)
        response.status = status_code
        response.read.return_value = body
        response.reason = reason

        response.getheaders.return_value = header
        response.msg = dict(header)

        def overwrite_header(arg, default=None):
            header_dict = dict(header)
            if header_dict.has_key(arg):
                return header_dict[arg]
            else:
                return default

        response.getheader.side_effect = overwrite_header

        return response

    def assert_request_parameters(self, params, ignore_params_values=None):
        """Verify the actual parameters sent to the service API."""
        request_params = self.actual_request.params.copy()
        if ignore_params_values is not None:
            for param in ignore_params_values:
                try:
                    del request_params[param]
                except KeyError:
                    pass
        assert request_params == params

    def set_http_response(self, status_code, reason='', header=[], body=None):
        http_response = self.create_response(status_code, reason, header, body)
        self.https_connection.getresponse.return_value = http_response

    def default_body(self):
        return ''


# ------------------------------------------------------------------------------------------


class TestExportSnapshot(AWSMockServiceTestCase):
    connection_class = fcu.FCUConnection

    def default_body(self):
        return """\
<?xml version="1.0"?>
<CreateSnapshotExportTaskResponse xmlns="http://ec2.amazonaws.com/doc/2013-10-15/">
  <requestId>8f16a797-df3b-42a3-861d-1b3d0e2f7281</requestId>
  <snapshotExportTask>
    <snapshotExportTaskId>snap-export-4c79c354</snapshotExportTaskId>
    <state>failed</state>
    <statusMessage>An error</statusMessage>
    <snapshotExport>
      <snapshotId>snap-fa2e5260</snapshotId>
    </snapshotExport>
    <exportToOsu>
      <diskImageFormat>qcow2</diskImageFormat>
      <osuBucket>odt-export-test</osuBucket>
      <osuKey>exports/snap-export-4c79c354.qcow2</osuKey>
    </exportToOsu>
  </snapshotExportTask>
</CreateSnapshotExportTaskResponse>
"""

    def test_export_snapshot(self):
        self.set_http_response(status_code=200)
        api_response = self.service_connection.export_snapshot(
            snapshot_id='snapshot-12345678',
            disk_image_format='qcow2',
            bucket='test-export',
            prefix='exports/'
        )

        self.assert_request_parameters({
                                           'Action': 'CreateSnapshotExportTask',
                                           'SnapshotId': 'snapshot-12345678',
                                           'ExportToOsu.DiskImageFormat': 'qcow2',
                                           'ExportToOsu.OsuBucket': 'test-export',
                                           'ExportToOsu.OsuPrefix': 'exports/',
                                       }, ignore_params_values=[
            'AWSAccessKeyId', 'SignatureMethod',
            'SignatureVersion', 'Timestamp',
            'Version'
        ])

        assert isinstance(api_response, fcu.SnapshotExportTask)
        assert api_response.id == 'snap-export-4c79c354'
        assert api_response.state == 'failed'
        assert api_response.status_message == 'An error'
        assert api_response.snapshot_id == 'snap-fa2e5260'
        assert api_response.disk_image_format == 'qcow2'
        assert api_response.bucket == 'odt-export-test'
        assert api_response.key == 'exports/snap-export-4c79c354.qcow2'


class TestGetAllSnapshotExports(AWSMockServiceTestCase):
    connection_class = fcu.FCUConnection

    def default_body(self):
        return """\
<?xml version="1.0"?>
<DescribeSnapshotExportTasksResponse xmlns="http://ec2.amazonaws.com/doc/2013-10-15/">
  <requestId>8f16a797-df3b-42a3-861d-1b3d0e2f7281</requestId>
  <snapshotExportTaskSet>
    <item>
      <snapshotExportTaskId>snap-export-4c79c354</snapshotExportTaskId>
      <state>failed</state>
      <statusMessage>An error</statusMessage>
      <snapshotExport>
        <snapshotId>snap-fa2e5260</snapshotId>
      </snapshotExport>
      <exportToOsu>
        <diskImageFormat>qcow2</diskImageFormat>
        <osuBucket>odt-export-test</osuBucket>
        <osuKey>exports/snap-export-4c79c354.qcow2</osuKey>
      </exportToOsu>
    </item>
    <item>
      <snapshotExportTaskId>snap-export-75481254</snapshotExportTaskId>
      <state>active</state>
      <snapshotExport>
        <snapshotId>snap-bef4512d</snapshotId>
      </snapshotExport>
      <exportToOsu>
        <diskImageFormat>qcow2</diskImageFormat>
        <osuBucket>odt-export-test</osuBucket>
        <osuKey>exports/snap-export-4c79c354.qcow2</osuKey>
      </exportToOsu>
    </item>
  </snapshotExportTaskSet>
</DescribeSnapshotExportTasksResponse>
"""

    def test_export_snapshot(self):
        self.set_http_response(status_code=200)
        api_response = self.service_connection.get_all_snapshot_export_tasks(
            ['snap-export-4c79c354', 'snap-export-75481254'],
            filters={'filer1': ['value1', 'value2']}
        )

        self.assert_request_parameters({
                                           'Action': 'DescribeSnapshotExportTasks',
                                           'SnapshotExportTaskId.1': 'snap-export-4c79c354',
                                           'SnapshotExportTaskId.2': 'snap-export-75481254',
                                           'Filter.1.Name': 'filer1',
                                           'Filter.1.Value.1': 'value1',
                                           'Filter.1.Value.2': 'value2'
                                       }, ignore_params_values=[
            'AWSAccessKeyId', 'SignatureMethod',
            'SignatureVersion', 'Timestamp',
            'Version'
        ])

        assert isinstance(api_response, list)
        assert len(api_response) == 2
        task1 = api_response[0]
        task2 = api_response[1]

        assert isinstance(task1, fcu.SnapshotExportTask)
        assert task1.id == 'snap-export-4c79c354'
        assert task1.state == 'failed'
        assert task1.status_message == 'An error'
        assert task1.snapshot_id == 'snap-fa2e5260'
        assert task1.disk_image_format == 'qcow2'
        assert task1.bucket == 'odt-export-test'
        assert task1.key == 'exports/snap-export-4c79c354.qcow2'

        assert isinstance(task2, fcu.SnapshotExportTask)


class TestGetProductType(AWSMockServiceTestCase):
    connection_class = fcu.FCUConnection

    def default_body(self):
        return """\
<?xml version="1.0"?>
<GetProductTypeResponse xmlns="http://ec2.amazonaws.com/doc/2013-10-15/">
  <productTypeId>0001</productTypeId>
  <description>Linux/UNIX</description>
</GetProductTypeResponse>
"""

    def test_export_snapshot(self):
        self.set_http_response(status_code=200)
        api_response = self.service_connection.get_product_type(
            snapshot_id='snap-4c79c354'
        )

        self.assert_request_parameters({
                                           'Action': 'GetProductType',
                                           'SnapshotId': 'snap-4c79c354',
                                           'ImageId': None
                                       }, ignore_params_values=[
            'AWSAccessKeyId', 'SignatureMethod',
            'SignatureVersion', 'Timestamp',
            'Version'
        ])

        assert isinstance(api_response, fcu.ProductType)
        assert api_response.id == '0001'
        assert api_response.description == 'Linux/UNIX'

        self.set_http_response(status_code=200)
        api_response = self.service_connection.get_product_type(
            image_id='ami-4c79c354'
        )

        self.assert_request_parameters({'Action': 'GetProductType', 'SnapshotId': None, 'ImageId': 'ami-4c79c354', },
                                       ignore_params_values=[
                                           'AWSAccessKeyId', 'SignatureMethod', 'SignatureVersion', 'Timestamp',
                                           'Version',
                                       ])


class TestDescribeCatalogs(AWSMockServiceTestCase):
    connection_class = fcu.FCUConnection

    def default_body(self):
        return """\
<?xml version="1.0"?>
<DescribeCatalogsResponse xmlns="http://ec2.amazonaws.com/doc/2013-10-15/">
    <requestId>da556ea1-f991-464b-9fa8-7f00c9043fa2</requestId>
    <catalogSet>
        <item>
            <attributeSet>
                <item><key>titi</key><value>tutu</value></item>
                <item><key>currency</key><value>EUR</value></item>
            </attributeSet>
            <entrySet>
                <item>
                    <key>first_set</key>
                    <attributeSet>
                        <item><key>key1</key><value>value1</value></item>
                        <item><key>key2</key><value>value2</value></item>
                    </attributeSet>
                    <valueSet>
                        <item>
                            <value>batman</value>
                        </item>
                        <item>
                            <value>superman</value>
                        </item>
                    </valueSet>
                </item>
                <item>
                    <key>second_set</key>
                    <attributeSet>
                        <item><key>key3</key><value>value3</value></item>
                        <item><key>key4</key><value>value4</value></item>
                    </attributeSet>
                    <valueSet>
                        <item>
                            <value>spiderman</value>
                            <tokens>
                                <item>token1</item>
                            </tokens>
                        </item>
                        <item>
                            <value>pacman</value>
                            <tokenSet>
                                <item>token1</item>
                                <item>token2</item>
                                <item>token3</item>
                            </tokenSet>
                        </item>
                    </valueSet>
                </item>
            </entrySet>
        </item>
    </catalogSet>
</DescribeCatalogsResponse>
"""

    def test_describe_catalogs(self):
        self.set_http_response(status_code=200)
        api_response = self.service_connection.get_all_catalogs()

        self.assert_request_parameters({'Action': 'DescribeCatalogs', },
                                       ignore_params_values=[
                                           'AWSAccessKeyId', 'SignatureMethod', 'SignatureVersion', 'Timestamp',
                                           'Version',
                                       ])

        assert isinstance(api_response, list)

        catalog = api_response[0]

        assert len(catalog.attributes) == 2
        assert catalog.attributes['titi'] == 'tutu'
        assert catalog.attributes['currency'] == 'EUR'

        assert len(catalog.entries) == 2
        assert catalog.entries[0].key == 'first_set'
        assert len(catalog.entries[0].attributes) == 2
        assert catalog.entries[0].attributes['key1'] == 'value1'

        assert len(catalog.entries[1].values) == 2
        assert catalog.entries[1].values[1].value == 'pacman'
        assert len(catalog.entries[1].values[1].tokens) == 3
        assert catalog.entries[1].values[1].tokens[2] == 'token3'


class TestDescribeInstanceTypes(AWSMockServiceTestCase):
    connection_class = fcu.FCUConnection

    def default_body(self):
        return """\
<?xml version="1.0" encoding="UTF-8"?>
<DescribeInstanceTypesResponse xmlns="http://ec2.amazonaws.com/doc/2014-10-15/">
  <requestId>71519976-8abb-4785-97f0-14df73bb1fad</requestId>
  <instanceTypeSet>
    <item>
      <name>m3.large</name>
      <vcpu>2</vcpu>
      <memory>8050966528</memory>
      <storageSize>34359738368</storageSize>
      <storageCount>1</storageCount>
      <maxIpAddresses>10</maxIpAddresses>
      <ebsOptimizedAvailable>true</ebsOptimizedAvailable>
    </item>
    <item>
      <name>oc2.8xlarge</name>
      <vcpu>15</vcpu>
      <memory>68718428160</memory>
      <maxIpAddresses>30</maxIpAddresses>
      <ebsOptimizedAvailable>false</ebsOptimizedAvailable>
    </item>
  </instanceTypeSet>
</DescribeInstanceTypesResponse>
"""

    def test_get_all_instance_types(self):
        self.set_http_response(status_code=200)
        api_response = self.service_connection.get_all_instance_types(filters={'name': 'oc2.8xlarge'})

        self.assert_request_parameters({'Action': 'DescribeInstanceTypes',
                                        'Filter.1.Name': 'name',
                                        'Filter.1.Value.1': 'oc2.8xlarge'},
                                       ignore_params_values=[
                                           'AWSAccessKeyId', 'SignatureMethod', 'SignatureVersion', 'Timestamp',
                                           'Version',
                                       ])

        assert isinstance(api_response, list)
        assert len(api_response) == 2

        type1 = api_response[0]
        type2 = api_response[1]

        assert type1.name == 'm3.large'
        assert type1.vcpu == 2
        assert type1.memory / 1024 ** 2 == 7678
        assert type1.storage_size == 34359738368
        assert type1.storage_count == 1
        assert type1.max_ip_addresses == 10
        assert type1.ebs_optimized_available is True

        assert type2.name == 'oc2.8xlarge'
        assert type2.vcpu == 15
        assert type2.memory == 68718428160
        assert type2.storage_size is None
        assert type2.storage_count is None
        assert type2.max_ip_addresses == 30
        assert type2.ebs_optimized_available is False


class TestDescribeProductTypes(AWSMockServiceTestCase):
    connection_class = fcu.FCUConnection

    def default_body(self):
        return """\
<?xml version="1.0" encoding="UTF-8"?>
<DescribeProductTypesResponse xmlns="http://ec2.amazonaws.com/doc/2014-10-15/">
    <requestId>71fc6180-6c37-411f-b519-577746cecb8c</requestId>
    <productTypeSet>
        <item>
            <productTypeId>0001</productTypeId>
            <description>Linux/UNIX</description>
        </item>
        <item>
             <productTypeId>0002</productTypeId>
             <description>Windows</description>
        </item>
    </productTypeSet>
</DescribeProductTypesResponse>
"""

    def test_get_all_product_types(self):
        self.set_http_response(status_code=200)
        api_response = self.service_connection.get_all_product_types(filters={'description': 'Linux/UNIX'})

        self.assert_request_parameters({'Action': 'DescribeProductTypes',
                                        'Filter.1.Name': 'description',
                                        'Filter.1.Value.1': 'Linux/UNIX'},
                                       ignore_params_values=[
                                           'AWSAccessKeyId', 'SignatureMethod', 'SignatureVersion', 'Timestamp',
                                           'Version',
                                       ])

        assert isinstance(api_response, list)
        assert len(api_response) == 2

        type1 = api_response[0]
        type2 = api_response[1]

        assert type1.id == '0001'
        assert type1.description == 'Linux/UNIX'

        assert type2.id == '0002'
        assert type2.description == 'Windows'
