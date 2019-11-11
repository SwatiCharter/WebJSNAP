from utility.utility import Utility
from importlib import import_module

# Abstraction layer for vendor-specific snapshotters
class SnapshotService:
    def snapshot(self, hostname):
        device_info = Utility.get_device_info(hostname)

        if device_info == None:
            return Utility.return_json(0, 'Invalid hostname or IP')

        class_path_name = Utility.get_vendor_models()[device_info['vendor']][device_info['model']]
        class_name = class_path_name.capitalize()

        # Dynamically import and instantiate the correct snapshot class
        module_name = import_module(f'drivers.snapshot.{device_info["vendor_lower"]}.{class_path_name}')
        class_ref = getattr(module_name, class_name)

        snapshot = class_ref()

        credentials = {
            'device_type': Utility.get_device_types()[device_info['vendor']],
            'host': hostname,
            'username': Utility.get_credentials()['username'],
            'password': Utility.get_credentials()['password']
        }

        return snapshot.snapshot(credentials)