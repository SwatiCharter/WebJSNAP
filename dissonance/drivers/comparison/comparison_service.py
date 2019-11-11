from drivers.comparison.jsnap import JSnapComparison
from utility.utility import Utility

class ComparisonService:

    def compare(self, hostname, presnap_timestamp, postsnap_timestamp):

        try:
            device_info = Utility.get_device_info(hostname)

            # Breaking DI by instantiating JSnapComparison here, but I don't foresee making a custom comparison engine for awhile.
            #  But for easier future proofing, I'm leaving this essentially useless class in the process, as it will serve
            #   as an abstraction layer when I do design my own comparison engine

            return Utility.return_json(1, "Compare()", JSnapComparison().compare(
                hostname,
                presnap_timestamp,
                postsnap_timestamp,
                Utility.get_vendor_models()[device_info['vendor']][device_info['model']]
            ))
        except Exception as e:
            return Utility.return_json(0, 'Failed - ensure you can access sense.one.twcbiz.com APIs')

    def get_snapshots(self, hostname):
        try:
            return Utility.return_json(1, 'get_snapshots()', JSnapComparison().get_snapshots(hostname))
        except Exception as e:
            return Utility.return_json(0, e.msg)

    def get_pre_and_post_snapshots(self, hostname):
        try:
            return Utility.return_json(1, 'get_pre_and_post_snapshots()', JSnapComparison().get_pre_and_post_snapshots(hostname))
        except Exception as e:
            return Utility.return_json(0, e.msg)

    def get_pre_snapshots(self, hostname):
        try:
            return Utility.return_json(1, 'get_pre_snapshots()', JSnapComparison().get_pre_snapshots(hostname))
        except Exception as e:
            return Utility.return_json(0, e.msg)

    def get_post_snapshots(self, hostname, starting_timestamp):
        return JSnapComparison().get_post_snapshots(hostname, starting_timestamp)

    def delete_snapshot(self, hostname, timestamp):
        return JSnapComparison().delete_snapshot(hostname, timestamp)
    