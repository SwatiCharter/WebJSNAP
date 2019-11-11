from netmiko import ConnectHandler
import yaml, json
from utility.utility import Utility
from lxml import etree
import time
from pprint import pprint
from importlib import import_module

class Cisco_xr():

    def snapshot(self, credentials):
        timestamp = time.time()
        hostname = credentials['host']

        test_file = Utility.load_yaml(f"testfiles/{credentials['device_type']}.yaml")

        dev = ConnectHandler(**credentials)

        output = ''
        for test in test_file:
            if 'command' not in test_file[test][0]:
                continue

            raw_command_name = str(test).replace('-', '_')
            #command = test_file[test][0]['command']


            module = import_module(f'drivers.snapshot.cisco.commands.{raw_command_name}')
            command_ref = getattr(module, raw_command_name)

            command_ref = command_ref()
            xml = command_ref.schemaify(
                        command_ref.parse(
                            dev.send_command(
                                command_ref.command()
                            )
                        )
                    )

            output = output + f"{hostname}@@@@{timestamp}@@@@{raw_command_name}@@@@{xml}@@@@@@"

        with open(f'snapshots/compiled_snapshots/{hostname}_{timestamp}.xml', 'w') as fp:
            fp.write(output)

        return Utility.return_json(True, 'Snapshot Completed')