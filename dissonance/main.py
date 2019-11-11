from flask import Flask
import os, sys
from drivers.snapshot.snapshot_service import SnapshotService
from drivers.comparison.comparison_service import ComparisonService
import json

os.environ['JSNAPY_HOME'] = sys.path[0]

app = Flask(__name__)
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/snapshot/<hostname>')
def snapshot(hostname):
    return SnapshotService().snapshot(hostname)

@app.route('/compare/<hostname>/<presnap>/<postsnap>')
def compare(hostname, presnap, postsnap):
    return ComparisonService().compare(hostname, presnap, postsnap)

@app.route('/get_pre_and_post_snapshots/<hostname>')
def get_pre_and_post_snapshots(hostname):
    return ComparisonService().get_pre_and_post_snapshots(hostname)

@app.route('/get_post_snapshots/<hostname>/<starting_timestamp>')
def get_post_snapshots(hostname, starting_timestamp):
    return ComparisonService().get_post_snapshots(hostname, starting_timestamp)

@app.route('/get_pre_snapshots/<hostname>')
def get_pre_snapshots(hostname):
    return ComparisonService().get_pre_snapshots(hostname)

@app.route('/get_snapshots/', defaults={'hostname': '*'})
@app.route('/get_snapshots/<hostname>')
def get_snapshots(hostname):
    return ComparisonService().get_snapshots(hostname)

@app.route('/delete_snapshot/<hostname>/<timestamp>')
def delete_snapshot(hostname, timestamp):
    return ComparisonService().delete_snapshot(hostname, timestamp)





















@app.route('/debug')
def debug():

    js = json.loads("")

    for test_name, test_data in js.items():

        for sub_test_data in test_data:

            if len(sub_test_data['failed']) > 0:
                print(sub_test_data['failed'][0]['message'])
if __name__ == '__main__':
    app.run()
