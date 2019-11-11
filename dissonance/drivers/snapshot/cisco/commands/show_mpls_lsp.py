class show_mpls_lsp:

    # HACK This isn't configured on the lab device yet, so I can't test it
    def command(self):
        return "show version"


    def parse(self, mpls_lsp_data):
        return {}


    def schemaify(self, data):
        xml = """
        <mpls-lsp-information>
        <rsvp-session-data>
            <session-type>Ingress</session-type>
            <count>0</count>
            <display-count>0</display-count>
            <up-count>0</up-count>
            <down-count>0</down-count>
        </rsvp-session-data>
        <rsvp-session-data>
            <session-type>Egress</session-type>
            <count>0</count>
            <display-count>0</display-count>
            <up-count>0</up-count>
            <down-count>0</down-count>
        </rsvp-session-data>
        <rsvp-session-data>
            <session-type>Transit</session-type>
            <count>0</count>
            <display-count>0</display-count>
            <up-count>0</up-count>
            <down-count>0</down-count>
        </rsvp-session-data>
    </mpls-lsp-information>  
        """

        return xml