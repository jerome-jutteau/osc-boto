############
osc-boto-ext
############


************
Introduction
************

This package adds an extension to boto to access Outscale specific APIs.

******
Usage
******

Use the function *connect_fcu_region* to create a connection object: ::

   >>> from outscale.boto import fcu
   >>> conn = fcu.connect_fcu_endpoint('fcu.eu-west-2.outscale.com',
                                       aws_access_key_id=AK,
                                       aws_secret_access_key=SK)


Connection can then be use to access both EC2 and OWS specific APIs, e.g.: ::

   >>> snap = conn.get_all_snapshots(owner='self')[0]
   >>> export_task = conn.export_snapshots(snap.id, 'bucket', 'qcow2')



******************
Outscale API Calls
******************

*export_snapshot* (snapshot_id, bucket, disk_image_format)

  Export a snapshot to a OSU bucket

  *Parameters*:

    * *snapshot_id*: Snapshot ID to export
    * *bucket*: Bucket to export to, bucket must exist and allow write access to Outscale account.
    * *disk_image_format*: The export format: vmdk vdi qcow2
    * *prefix*: Prefix of the destination key in the bucket, snapshot will be written to prefix + snapshot_export_task_id + '.' + disk_image_format.

  *Returns*: A task object with fields:
    * *id*: Task identifier, may be passed to *get_all_snapshot_export_task*
    * *snapshot_id*: ID of snapshot being exported
    * *state*: State of the task, either 'pending', 'active', 'completed' or 'failed'
    * *status_message*: If export task failed, an error message
    * *bucket*: Name of the OSU bucket snapshot is being exported
    * *key*: Name of OSU key where snpashot is being exported


*get_all_snapshot_export_tasks* (task_ids)

  Get all snapshot export tasks

  *Parameters*:
    * *task_ids*: A list of task IDs to retrieve

  *Returns*: A list of task objects


*get_all_instance_types* ()

  Retrieve definition of instance types

  *Returns*: A list of instance types with fields:
    * *name*: Instance type name (e.g. t1.micro)
    * *vcpu*: Number of VCPU
    * *memory*: Amount of memory in bytes
    * *storage_size*: Size of ephemerals disks in bytes
    * *storage_count*: Maximum ephemerals disks that may be attached
    * *max_ip_addresses*: Maximum number of private IP addresses that may be attached
    * *ebs_optimized_available*: Whether this instance type may be started in EBS optimized mode
