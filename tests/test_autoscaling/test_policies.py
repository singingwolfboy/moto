import boto
from boto.ec2.autoscale.launchconfig import LaunchConfiguration
from boto.ec2.autoscale.group import AutoScalingGroup
from boto.ec2.autoscale.policy import ScalingPolicy
import sure  # flake8: noqa

from moto import mock_autoscaling, mock_ec2


def setup_autoscale_group():
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
    return group


@mock_autoscaling
def test_create_policy():
    group = setup_autoscale_group()
    conn = boto.connect_autoscale()
    policy = ScalingPolicy(
        name='ScaleUp',
        adjustment_type='ExactCapacity',
        as_name='tester_group',
        scaling_adjustment=3,
        cooldown=60,
    )
    conn.create_scaling_policy(policy)

    policy = conn.get_all_policies()[0]
    policy.name.should.equal('ScaleUp')
    policy.adjustment_type.should.equal('ExactCapacity')
    policy.as_name.should.equal('tester_group')
    policy.scaling_adjustment.should.equal(3)
    policy.cooldown.should.equal(60)


@mock_autoscaling
def test_create_policy_default_values():
    group = setup_autoscale_group()
    conn = boto.connect_autoscale()
    policy = ScalingPolicy(
        name='ScaleUp',
        adjustment_type='ExactCapacity',
        as_name='tester_group',
        scaling_adjustment=3,
    )
    conn.create_scaling_policy(policy)

    policy = conn.get_all_policies()[0]
    policy.name.should.equal('ScaleUp')

    # Defaults
    policy.cooldown.should.equal(300)


@mock_autoscaling
def test_update_policy():
    group = setup_autoscale_group()
    conn = boto.connect_autoscale()
    policy = ScalingPolicy(
        name='ScaleUp',
        adjustment_type='ExactCapacity',
        as_name='tester_group',
        scaling_adjustment=3,
    )
    conn.create_scaling_policy(policy)

    policy = conn.get_all_policies()[0]
    policy.scaling_adjustment.should.equal(3)

    # Now update it by creating another with the same name
    policy = ScalingPolicy(
        name='ScaleUp',
        adjustment_type='ExactCapacity',
        as_name='tester_group',
        scaling_adjustment=2,
    )
    conn.create_scaling_policy(policy)
    policy = conn.get_all_policies()[0]
    policy.scaling_adjustment.should.equal(2)


@mock_autoscaling
def test_delete_policy():
    group = setup_autoscale_group()
    conn = boto.connect_autoscale()
    policy = ScalingPolicy(
        name='ScaleUp',
        adjustment_type='ExactCapacity',
        as_name='tester_group',
        scaling_adjustment=3,
    )
    conn.create_scaling_policy(policy)

    conn.get_all_policies().should.have.length_of(1)

    conn.delete_policy('ScaleUp')
    conn.get_all_policies().should.have.length_of(0)
