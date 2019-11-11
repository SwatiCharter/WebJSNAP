from dateutil.parser import parse as is_this_a_date

class show_bgp_summary:

    def command(self):
        # yikes, so "show bgp summary" on Juniper gives us the info we need, but on Cisco, we can only get
        #  the neighborship state, peer AS, etc... from show bgp neighbors. This will definitely cause confusion
        return "show bgp neighbors"


    def parse(self, bgp_neighbors_data):
        bgp_neighbors = str(bgp_neighbors_data).split('BGP neighbor is ')

        if is_this_a_date(bgp_neighbors[0]):
            del bgp_neighbors[0]

        dict_neighbors = {}
        for neighbor in bgp_neighbors:
            peer_address = neighbor.split('\n')[0].strip()
            peer_as = neighbor.split('Remote AS ')[1].split(',')[0].strip()
            peer_state = neighbor.split('BGP state = ')[1].split()[0].strip(',').strip()
            dict_neighbors[peer_address] = {
                'peer-state': peer_state,
                'peer-as': peer_as
            }
        return dict_neighbors


    def schemaify(self, data):
        xml = ""
        for peer_address, neighbor in data.items():
            xml += """
                <bgp-peer>
                    <peer-address>%s</peer-address>
                    <peer-as>%s</peer-as>
                    <peer-state>%s</peer-state>
                </bgp-peer>
                """ % (peer_address, neighbor['peer-as'], neighbor['peer-state'])

        xml = """
        <bgp-information>
        %s
        </bgp-information>
         """ % xml

        return xml