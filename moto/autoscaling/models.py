from moto.core import BaseBackend


class FakeLaunchConfiguration(object):
    def __init__(self, name, image_id, key_name, security_groups, user_data,
                 instance_type, instance_monitoring, instance_profile_name,
                 spot_price, ebs_optimized):
        self.name = name
        self.image_id = image_id
        self.key_name = key_name
        self.security_groups = security_groups
        self.user_data = user_data
        self.instance_type = instance_type
        self.instance_monitoring = instance_monitoring
        self.instance_profile_name = instance_profile_name
        self.spot_price = spot_price
        self.ebs_optimized = ebs_optimized

    @property
    def instance_monitoring_enabled(self):
        if self.instance_monitoring:
            return 'true'
        return 'false'


class AutoScalingBackend(BaseBackend):

    def __init__(self):
        self.launch_configurations = {}

    def create_launch_configuration(self, name, image_id, key_name,
                                    security_groups, user_data, instance_type,
                                    instance_monitoring, instance_profile_name,
                                    spot_price, ebs_optimized):
        launch_configuration = FakeLaunchConfiguration(
            name=name,
            image_id=image_id,
            key_name=key_name,
            security_groups=security_groups,
            user_data=user_data,
            instance_type=instance_type,
            instance_monitoring=instance_monitoring,
            instance_profile_name=instance_profile_name,
            spot_price=spot_price,
            ebs_optimized=ebs_optimized,
        )
        self.launch_configurations[name] = launch_configuration
        return launch_configuration

    def describe_launch_configurations(self, names):
        configurations = self.launch_configurations.values()
        if names:
            return [configuration for configuration in configurations if configuration.name in names]
        else:
            return configurations

    def delete_launch_configuration(self, launch_configuration_name):
        self.launch_configurations.pop(launch_configuration_name, None)


autoscaling_backend = AutoScalingBackend()
