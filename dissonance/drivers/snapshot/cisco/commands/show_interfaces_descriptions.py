from dateutil.parser import parse as is_this_a_date

class show_interfaces_descriptions:

    def command(self):
        return "show interfaces description"


    def parse(self, interfaces_data):
        interfaces_data = str(interfaces_data).split('--------------------------------------------------------------------------------')

        interfaces = set(interfaces_data[1].split("\n"))
        interfaces = filter(None, interfaces)
        thedata = {}

        for interface in interfaces:

            interface = interface.split(None, 3)

            if 3 not in interface: interface.append("")

            thedata[interface[0]] = {
                'admin-status': interface[1],
                'oper-status': interface[2],
                'description': interface[3]
            }


        return thedata


    def schemaify(self, data):
        xml = ""
        for interface_name, interface_data in data.items():

            interface_type = "physical-interface"
            if "." in interface_name: # logical interface
                interface_type = "logical-interface"


            xml +=    f"""
                            <{interface_type}>
                                <name>{interface_name}</name>
                                <admin-status>{interface_data['admin-status']}</admin-status>
                                <oper-status>{interface_data['oper-status']}</oper-status>
                                <description>{interface_data['description']}</description>
                            </{interface_type}>
                        """

        xml = """
        <interface-information>
        %s
        </interface-information>
         """ % xml

        return xml

