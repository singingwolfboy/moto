from jinja2 import Template

from moto.core.responses import BaseResponse
from .models import autoscaling_backend


class AutoScalingResponse(BaseResponse):

    def _get_param(self, param_name):
        return self.querystring.get(param_name, [None])[0]

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
            ebs_optimized=self._get_param('EbsOptimized'),
        )
        template = Template(CREATE_LAUNCH_CONFIGURATION_TEMPLATE)
        return template.render()

    def describe_launch_configurations(self):
        names = [value[0] for key, value in self.querystring.items()
                 if key.startswith("LaunchConfigurationNames")]
        launch_configurations = autoscaling_backend.describe_launch_configurations(names)
        template = Template(DESCRIBE_LAUNCH_CONFIGURATIONS_TEMPLATE)
        return template.render(launch_configurations=launch_configurations)

    def delete_launch_configuration(self):
        launch_configurations_name = self.querystring.get('LaunchConfigurationName')[0]
        autoscaling_backend.delete_launch_configuration(launch_configurations_name)
        template = Template(DELETE_LAUNCH_CONFIGURATION_TEMPLATE)
        return template.render()


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
          <EbsOptimized>{{ launch_configuration.ebs_optimized }}</EbsOptimized>
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
