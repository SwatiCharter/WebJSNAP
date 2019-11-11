import yaml
import json
import requests
import os
class Utility:

    @staticmethod
    def get_device_types():
        return Utility.load_yaml('config/device_types.yaml')

    @staticmethod
    def get_credentials():
        return Utility.load_yaml('config/credentials.yaml')

    @staticmethod
    def get_vendor_models():
        return Utility.load_yaml('config/vendor_models.yaml')

    @staticmethod
    def load_yaml(filepath):
        return yaml.safe_load(open(filepath).read())


    @staticmethod
    def return_json(success=True, message="", payload=None):
        return json.dumps({
            'success': success,
            'message': message,
            'payload': payload
        })

    @staticmethod
    def get_device_info(hostname):
        r = requests.get(url=Utility.load_yaml('config/settings.yaml')['device_info_url'] + hostname, timeout=10).json()

        # @TODO: code is super weird here at the moment because I'm refactoring some things, will clean this up later
        if len(r) == 0:
            return None # this specifically... no longer need to return None but should throw exception here

        device_info = r[0]

        vendor = device_info['VENDOR']
        vendor_lower = str(vendor).lower()
        model = device_info['MODEL']


        if vendor not in Utility.get_vendor_models():
            return Utility.return_json(False, 'Invalid vendor returned for device')

        if model not in Utility.get_vendor_models()[vendor]:
            model = '*'

        return {
            'vendor': device_info['VENDOR'],
            'vendor_lower': vendor_lower,
            'model': model
        }

    @staticmethod
    def is_file_path_safe(file_path):
        file_path = os.path.normpath(file_path)
        if '..' in file_path or '/' in file_path or '\\' in file_path:
            return False

        return True