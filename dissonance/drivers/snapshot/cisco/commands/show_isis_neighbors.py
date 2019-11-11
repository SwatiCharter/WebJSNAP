from dateutil.parser import parse as is_this_a_date

class show_isis_neighbors:

    def command(self):
        return "show isis neighbors"


    def parse(self, neighbors_data):
        neighbors_data = str(neighbors_data).split('IS-IS default neighbors:')[1].split('\n')
        neighbors_data.pop(0)
        neighbors_data.pop(0)

        neighbor_dict = {}
        for neighbor in neighbors_data:
            neighbor = ' '.join(neighbor.split()).split(' ')
            if len(neighbor) != 7:
                continue

            neighbor_dict[neighbor[1]] = {
                'system-name': neighbor[0],
                'level': neighbor[5],
                'adjacency-state': neighbor[3],
                'holdtime': neighbor[4],
                'snpa': neighbor[2]
            }


        return neighbor_dict


    def schemaify(self, data):
        xml = ""
        for interface_name, neighbor_data in data.items():


            xml +=    f"""
                            <isis-adjacency>
                                <interface-name>{interface_name}</interface-name>
                                <system-name>{neighbor_data['system-name']}</system-name>
                                <level>{neighbor_data['level']}</level>
                                <adjacency-state>{neighbor_data['adjacency-state']}</adjacency-state>
                                <holdtime>{neighbor_data['holdtime']}</holdtime>
                                <snpa>{neighbor_data['snpa']}</snpa>
                            </isis-adjacency>
                        """

        xml = """
        <isis-adjacency-information>
        %s
        </isis-adjacency-information>
         """ % xml

        return xml
