from netmiko import ConnectHandler
from utility.utility import Utility
from lxml import etree
import time

import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

class Juniper:

    def __init__(self):
        pass

    def snapshot(self, credentials):
        timestamp = time.time()
        hostname = credentials['host']

        test_file = Utility.load_yaml('testfiles/juniper.yaml')

        dev = ConnectHandler(**credentials)

        output = ''
        for test in test_file:
            if 'command' not in test_file[test][0]:
                continue

            raw_command_name = str(test).replace('-', '_')
            command = test_file[test][0]['command']
            if ' | display xml' not in command:
                command = command + ' | display xml'

            result = str(dev.send_command(command)).strip('{master}').strip()

            xml = etree.fromstring(result).xpath('//rpc-reply/*[not(self::cli)]')

            if len(xml) <= 0:
                return Utility.return_json(False, 'Invalid rpc-reply from device')

            xml = etree.tostring(xml[0]).decode("utf-8")

            output = output + f"{hostname}@@@@{timestamp}@@@@{raw_command_name}@@@@{xml}@@@@@@"

        with open(f'snapshots/compiled_snapshots/{hostname}_{timestamp}.xml', 'w') as fp:
            fp.write(output)

        return Utility.return_json(True, 'Snapshot Completed')