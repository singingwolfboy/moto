from jinja2 import Template

from moto.core.responses import BaseResponse
from .models import autoscaling_backend


class AutoScalingResponse(BaseResponse):

    def _get_param(self, param_name):
        return self.querystring.get(param_name, [None])[0]

    def _get_int_param(self, param_name):
        value = self._get_param(param_name)
        if value is not None:
            return int(value)

    def _get_multi_param(self, param_prefix):
        return [value[0] for key, value in self.querystring.items() if key.startswith(param_prefix)]

    def create_launch_configuration(self):
        instance_monitoring_string = self._get_param('InstanceMonitoring.Enabled')
        if instance_monitoring_string == 'true':
            instance_monitoring = True
        else:
            instance_monitoring = False
        autoscaling_backend.create_launch_configuration(
            name=self._get_param('LaunchConfigurationName'),
            image_id=self._get_param('ImageId'),
            key_name=self._get_param('KeyName'),
            security_groups=self._get_multi_param('SecurityGroups.member.'),
            user_data=self._get_param('UserData'),
            instance_type=self._get_param('InstanceType'),
            instance_monitoring=instance_monitoring,
            instance_profile_name=self._get_param('IamInstanceProfile'),
            spot_price=self._get_param('SpotPrice'),
        )
        template = Template(CREATE_LAUNCH_CONFIGURATION_TEMPLATE)
        return template.render()

    def describe_launch_configurations(self):
        names = self._get_multi_param('LaunchConfigurationNames')
        launch_configurations = autoscaling_backend.describe_launch_configurations(names)
        template = Template(DESCRIBE_LAUNCH_CONFIGURATIONS_TEMPLATE)
        return template.render(launch_configurations=launch_configurations)

    def delete_launch_configuration(self):
        launch_configurations_name = self.querystring.get('LaunchConfigurationName')[0]
        autoscaling_backend.delete_launch_configuration(launch_configurations_name)
        template = Template(DELETE_LAUNCH_CONFIGURATION_TEMPLATE)
        return template.render()

    def create_auto_scaling_group(self):
        autoscaling_backend.create_autoscaling_group(
            name=self._get_param('AutoScalingGroupName'),
            availability_zones=self._get_multi_param('AvailabilityZones.member'),
            desired_capacity=self._get_int_param('DesiredCapacity'),
            max_size=self._get_int_param('MaxSize'),
            min_size=self._get_int_param('MinSize'),
            launch_config_name=self._get_param('LaunchConfigurationName'),
            vpc_zone_identifier=self._get_param('VPCZoneIdentifier'),
        )
        template = Template(CREATE_AUTOSCALING_GROUP_TEMPLATE)
        return template.render()

    def describe_auto_scaling_groups(self):
        names = self._get_multi_param("AutoScalingGroupNames")
        groups = autoscaling_backend.describe_autoscaling_groups(names)
        template = Template(DESCRIBE_AUTOSCALING_GROUPS_TEMPLATE)
        return template.render(groups=groups)

    def delete_auto_scaling_group(self):
        group_name = self._get_param('AutoScalingGroupName')
        autoscaling_backend.delete_autoscaling_group(group_name)
        template = Template(DELETE_AUTOSCALING_GROUP_TEMPLATE)
        return template.render()

    def describe_auto_scaling_instances(self):
        instances = autoscaling_backend.describe_autoscaling_instances()
        template = Template(DESCRIBE_AUTOSCALING_INSTANCES_TEMPLATE)
        return template.render(instances=instances)


CREATE_LAUNCH_CONFIGURATION_TEMPLATE = """<CreateLaunchConfigurationResponse xmlns="http://autoscaling.amazonaws.com/doc/2011-01-01/">
<ResponseMetadata>
   <RequestId>7c6e177f-f082-11e1-ac58-3714bEXAMPLE</RequestId>
</ResponseMetadata>
</CreateLaunchConfigurationResponse>"""

DESCRIBE_LAUNCH_CONFIGURATIONS_TEMPLATE = """<DescribeLaunchConfigurationsResponse xmlns="http://autoscaling.amazonaws.com/doc/2011-01-01/">
  <DescribeLaunchConfigurationsResult>
    <LaunchConfigurations>
      {% for launch_configuration in launch_configurations %}
        <member>
          <SecurityGroups>
            {% for security_group in launch_configuration.security_groups %}
              <member>{{ security_group }}</member>
            {% endfor %}
          </SecurityGroups>
          <CreatedTime>2013-01-21T23:04:42.200Z</CreatedTime>
          <KernelId/>
          {% if launch_configuration.instance_profile_name %}
            <IamInstanceProfile>{{ launch_configuration.instance_profile_name }}</IamInstanceProfile>
          {% endif %}
          <LaunchConfigurationName>{{ launch_configuration.name }}</LaunchConfigurationName>
          {% if launch_configuration.user_data %}
            <UserData>{{ launch_configuration.user_data }}</UserData>
          {% else %}
            <UserData/>
          {% endif %}
          <InstanceType>m1.small</InstanceType>
          <LaunchConfigurationARN>arn:aws:autoscaling:us-east-1:803981987763:launchConfiguration:
          9dbbbf87-6141-428a-a409-0752edbe6cad:launchConfigurationName/my-test-lc</LaunchConfigurationARN>
          <BlockDeviceMappings/>
          <ImageId>{{ launch_configuration.image_id }}</ImageId>
          {% if launch_configuration.key_name %}
            <KeyName>{{ launch_configuration.key_name }}</KeyName>
          {% else %}
            <KeyName/>
          {% endif %}
          <RamdiskId/>
          <InstanceMonitoring>
            <Enabled>{{ launch_configuration.instance_monitoring_enabled }}</Enabled>
          </InstanceMonitoring>
          {% if launch_configuration.spot_price %}
            <SpotPrice>{{ launch_configuration.spot_price }}</SpotPrice>
          {% endif %}
        </member>
      {% endfor %}
    </LaunchConfigurations>
  </DescribeLaunchConfigurationsResult>
  <ResponseMetadata>
    <RequestId>d05a22f8-b690-11e2-bf8e-2113fEXAMPLE</RequestId>
  </ResponseMetadata>
</DescribeLaunchConfigurationsResponse>"""

DELETE_LAUNCH_CONFIGURATION_TEMPLATE = """<DeleteLaunchConfigurationResponse xmlns="http://autoscaling.amazonaws.com/doc/2011-01-01/">
  <ResponseMetadata>
    <RequestId>7347261f-97df-11e2-8756-35eEXAMPLE</RequestId>
  </ResponseMetadata>
</DeleteLaunchConfigurationResponse>"""

CREATE_AUTOSCALING_GROUP_TEMPLATE = """<CreateAutoScalingGroupResponse xmlns="http://autoscaling.amazonaws.com/doc/2011-01-01/">
<ResponseMetadata>
<RequestId>8d798a29-f083-11e1-bdfb-cb223EXAMPLE</RequestId>
</ResponseMetadata>
</CreateAutoScalingGroupResponse>"""

DESCRIBE_AUTOSCALING_GROUPS_TEMPLATE = """<DescribeAutoScalingGroupsResponse xmlns="http://autoscaling.amazonaws.com/doc/2011-01-01/">
<DescribeAutoScalingGroupsResult>
    <AutoScalingGroups>
      {% for group in groups %}
      <member>
        <Tags/>
        <SuspendedProcesses/>
        <AutoScalingGroupName>{{ group.name }}</AutoScalingGroupName>
        <HealthCheckType>ELB</HealthCheckType>
        <CreatedTime>2013-05-06T17:47:15.107Z</CreatedTime>
        <EnabledMetrics/>
        <LaunchConfigurationName>{{ group.launch_config_name }}</LaunchConfigurationName>
        <Instances/>
        <DesiredCapacity>{{ group.desired_capacity }}</DesiredCapacity>
        <AvailabilityZones>
          {% for availability_zone in group.availability_zones %}
          <member>{{ availability_zone }}</member>
          {% endfor %}
        </AvailabilityZones>
        <LoadBalancerNames>
          <member>my-test-asg-loadbalancer</member>
        </LoadBalancerNames>
        <MinSize>{{ group.min_size }}</MinSize>
        {% if group.vpc_zone_identifier %}
          <VPCZoneIdentifier>{{ group.vpc_zone_identifier }}</VPCZoneIdentifier>
        {% else %}
          <VPCZoneIdentifier/>
        {% endif %}
        <HealthCheckGracePeriod>120</HealthCheckGracePeriod>
        <DefaultCooldown>300</DefaultCooldown>
        <AutoScalingGroupARN>arn:aws:autoscaling:us-east-1:803981987763:autoScalingGroup:ca861182-c8f9-4ca7-b1eb-cd35505f5ebb
        :autoScalingGroupName/my-test-asg-lbs</AutoScalingGroupARN>
        <TerminationPolicies>
          <member>Default</member>
        </TerminationPolicies>
        <MaxSize>{{ group.max_size }}</MaxSize>
      </member>
      {% endfor %}
    </AutoScalingGroups>
  </DescribeAutoScalingGroupsResult>
  <ResponseMetadata>
    <RequestId>0f02a07d-b677-11e2-9eb0-dd50EXAMPLE</RequestId>
  </ResponseMetadata>
</DescribeAutoScalingGroupsResponse>"""

DELETE_AUTOSCALING_GROUP_TEMPLATE = """<DeleteAutoScalingGroupResponse xmlns="http://autoscaling.amazonaws.com/doc/2011-01-01/">
  <ResponseMetadata>
    <RequestId>70a76d42-9665-11e2-9fdf-211deEXAMPLE</RequestId>
  </ResponseMetadata>
</DeleteAutoScalingGroupResponse>"""

DESCRIBE_AUTOSCALING_INSTANCES_TEMPLATE = """<DescribeAutoScalingInstancesResponse xmlns="http://autoscaling.amazonaws.com/doc/2011-01-01/">
  <DescribeAutoScalingInstancesResult>
    <AutoScalingInstances>
      {% for instance in instances %}
      <member>
        <HealthStatus>HEALTHY</HealthStatus>
        <AutoScalingGroupName>{{ instance.autoscaling_group.name }}</AutoScalingGroupName>
        <AvailabilityZone>us-east-1e</AvailabilityZone>
        <InstanceId>{{ instance.id }}</InstanceId>
        <LaunchConfigurationName>{{ instance.autoscaling_group.launch_config_name }}</LaunchConfigurationName>
        <LifecycleState>InService</LifecycleState>
      </member>
      {% endfor %}
    </AutoScalingInstances>
  </DescribeAutoScalingInstancesResult>
  <ResponseMetadata>
    <RequestId>df992dc3-b72f-11e2-81e1-750aa6EXAMPLE</RequestId>
  </ResponseMetadata>
</DescribeAutoScalingInstancesResponse>"""
