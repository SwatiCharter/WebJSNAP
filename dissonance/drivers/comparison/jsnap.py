import json
from jnpr.jsnapy.jsnapy import SnapAdmin
import os
from utility.utility import Utility
from glob import glob
from collections import OrderedDict
from pprint import pprint

class JSnapComparison:
    def generate_credentials(self):
        cred = Utility.load_yaml('config/credentials.yaml')
        return (cred['username'], cred['password'])

    # @TODO: Ugly, will do this properly later
    def generate_config(self, device, device_model):
        (username, password) = self.generate_credentials()

        config_data = f"""
                hosts:
                 - device: {device}
                   username: {username}
                   passwd: {password}
                tests:
                 - {device_model}.yaml"""

        return config_data.encode('ascii', 'ignore').decode('utf-8')

    def compare(self, hostname, presnap_timestamp, postsnap_timestamp, device_model):
        self.unpack(hostname, presnap_timestamp)
        self.unpack(hostname, postsnap_timestamp)

        check = SnapAdmin().check(str(self.generate_config(hostname, device_model)), pre_file=presnap_timestamp,
                         post_file=postsnap_timestamp, folder=os.environ['JSNAPY_HOME'])

        if len(check) <= 0:
            raise Exception('SnapAdmin() compare failed')

        self.unpack_cleanup(hostname, presnap_timestamp, postsnap_timestamp)


        # parse test_results into a normal / non-terrible structure for returning

        test_results = check[0].test_results
        pprint(test_results)
        final_results = OrderedDict()
        final_results['failedTests'] = {}
        for command_name, command_test_data in test_results.items():
            for test_data in command_test_data:
                if len(test_data['failed']) > 0:
                    if command_name not in final_results['failedTests']:
                        final_results['failedTests'][command_name] = []

                    for test in test_data['failed']:
                        final_results['failedTests'][command_name].append(test['message'])
                # else:
                #     for test in test_data['passed']:
                #         final_results['passedTests'].append(test['message'])

        return final_results

    def unpack(self, hostname, timestamp):
        with open(f'snapshots/compiled_snapshots/{hostname}_{timestamp}.xml', 'r') as fp:
            output = fp.read().strip()
           #f"{hostname}@@@@{timestamp}@@@@{raw_command_name}@@@@{xml}@@@@@@"
            tests = output.split('@@@@@@')[:-1]

            for test in tests:
                splits = test.split('@@@@')

                raw_command = splits[2]
                xml = splits[3]

                with open(f'snapshots/{hostname}_{timestamp}_{raw_command}.xml', 'w') as test_fp:
                    test_fp.write(str(xml).strip())

    def unpack_cleanup(self, hostname, presnap_timestamp, postsnap_timestamp):
        snap_files = glob(f"snapshots/{hostname}_{presnap_timestamp}_*.xml")
        snap_files.extend(glob(f"snapshots/{hostname}_{postsnap_timestamp}_*.xml"))

        for file in snap_files:
            os.remove(file)

    def get_snapshots(self, hostname):
        if not Utility.is_file_path_safe(hostname):
            raise Exception('Hostname was invalid')

        snap_files = sorted(glob(f"snapshots/compiled_snapshots/{hostname}_*.xml"), reverse=True)

        for iter, file in enumerate(snap_files):
            snap_files[iter] = (os.path.basename(str(file)))
            (temp_hostname, temp_timestamp) = snap_files[iter].split('_')
            temp_timestamp = temp_timestamp.strip('.xml')
            snap_files[iter] = [temp_hostname, temp_timestamp]
        return snap_files

    def get_pre_and_post_snapshots(self, hostname):
        presnaps = self.get_pre_snapshots(hostname)

        if len(presnaps) <= 0:
            raise Exception(f"No pre-snaps found for {hostname}")

        postsnaps = self.get_post_snapshots(hostname, presnaps[0][1])

        snapshots = {
            'presnaps': presnaps,
            'postsnaps': postsnaps
        }

        return snapshots


    def get_pre_snapshots(self, hostname):
        snapshots = self.get_snapshots(hostname)
        return snapshots[1:]

    def get_post_snapshots(self, hostname, starting_timestamp):
        snapshots = self.get_snapshots(hostname)

        final_snapshots = [x for x in snapshots if float(x[1]) > float(starting_timestamp)]

        return final_snapshots

    def delete_snapshot(self, hostname, timestamp):
        try:
            if not Utility.is_file_path_safe(hostname) or str(timestamp).count('.') > 1:
                return Utility.return_json(0, 'Invalid hostname')

            os.remove(f"snapshots/compiled_snapshots/{hostname}_{timestamp}.xml")

        except:
            return Utility.return_json(0, 'Unable to delete snapshot, probably non-existent')

        return Utility.return_json(1, 'Snapshot deleted')