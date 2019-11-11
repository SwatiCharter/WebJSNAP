from jnpr.junos.device import Device
import os

hostnames = filter(None, open('./hosts.txt', 'r').read().splitlines())
(username, password) = filter(None, open('./credentials.txt', 'r').read().splitlines())
for hostname in hostnames:
    with Device(host=hostname, user=username, passwd=password) as dev:

        set_commands = str(dev.cli('show configuration interfaces | display set')).strip().split('\n')
        set_commands = [s.strip() for s in set_commands]

        final_commands = []
        for command in set_commands:
            command = command.strip()

            if 'apply-groups DISABLEIF' in command:
                interface_name = command.split(' ')[2]
                # check if there's a disable for this interface
                if 'set interfaces ' + interface_name + ' disable' in set_commands:
                    final_commands.append('delete interfaces ' + interface_name + ' disable')


        # Outputs
        if not os.path.exists('./outputs'):
            os.mkdir('./outputs')

        output_name = './outputs/'+hostname

        if os.path.exists(output_name):
            os.remove(output_name)

        with open('./outputs/'+hostname, 'w') as fp:
            fp.write('\n'.join(final_commands))


        print "Finished - " + hostname


