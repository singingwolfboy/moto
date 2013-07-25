import boto
from boto.ec2.autoscale.launchconfig import LaunchConfiguration
from boto.ec2.autoscale.group import AutoScalingGroup

import sure  # flake8: noqa

from moto import mock_autoscaling


@mock_autoscaling
def test_create_autoscaling_group():
    conn = boto.connect_autoscale()
    config = LaunchConfiguration(
        name='tester',
        image_id='ami-abcd1234',
        instance_type='m1.small',
    )
    conn.create_launch_configuration(config)

    group = AutoScalingGroup(
        name='tester_group',
        availability_zones=['us-east-1c', 'us-east-1b'],
        desired_capacity=2,
        max_size=2,
        min_size=2,
        launch_config=config,
        vpc_zone_identifier='subnet-1234abcd',
    )
    conn.create_auto_scaling_group(group)

    group = conn.get_all_groups()[0]
    group.name.should.equal('tester_group')
    set(group.availability_zones).should.equal(set(['us-east-1c', 'us-east-1b']))
    group.desired_capacity.should.equal(2)
    group.max_size.should.equal(2)
    group.min_size.should.equal(2)
    group.vpc_zone_identifier.should.equal('subnet-1234abcd')
    group.launch_config_name.should.equal('tester')


@mock_autoscaling
def test_create_autoscaling_groups_defaults():
    """ Test with the minimum inputs and check that all of the proper defaults
    are assigned for the other attributes """
    conn = boto.connect_autoscale()
    config = LaunchConfiguration(
        name='tester',
        image_id='ami-abcd1234',
        instance_type='m1.small',
    )
    conn.create_launch_configuration(config)

    group = AutoScalingGroup(
        name='tester_group',
        max_size=2,
        min_size=2,
        launch_config=config,
    )
    conn.create_auto_scaling_group(group)

    group = conn.get_all_groups()[0]
    group.name.should.equal('tester_group')
    group.max_size.should.equal(2)
    group.min_size.should.equal(2)
    group.launch_config_name.should.equal('tester')

    # Defaults
    list(group.availability_zones).should.equal([])
    group.desired_capacity.should.equal(2)
    group.vpc_zone_identifier.should.equal('')


@mock_autoscaling
def test_autoscaling_group_describe_filter():
    conn = boto.connect_autoscale()
    config = LaunchConfiguration(
        name='tester',
        image_id='ami-abcd1234',
        instance_type='m1.small',
    )
    conn.create_launch_configuration(config)

    group = AutoScalingGroup(
        name='tester_group',
        max_size=2,
        min_size=2,
        launch_config=config,
    )
    conn.create_auto_scaling_group(group)
    group.name = 'tester_group2'
    conn.create_auto_scaling_group(group)
    group.name = 'tester_group3'
    conn.create_auto_scaling_group(group)

    conn.get_all_groups(names=['tester_group', 'tester_group2']).should.have.length_of(2)
    conn.get_all_groups().should.have.length_of(3)


@mock_autoscaling
def test_autoscaling_group_delete():
    conn = boto.connect_autoscale()
    config = LaunchConfiguration(
        name='tester',
        image_id='ami-abcd1234',
        instance_type='m1.small',
    )
    conn.create_launch_configuration(config)

    group = AutoScalingGroup(
        name='tester_group',
        max_size=2,
        min_size=2,
        launch_config=config,
    )
    conn.create_auto_scaling_group(group)

    conn.get_all_groups().should.have.length_of(1)

    conn.delete_auto_scaling_group('tester_group')
    conn.get_all_groups().should.have.length_of(0)
