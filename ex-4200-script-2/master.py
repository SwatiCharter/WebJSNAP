#!/opt/junosvenv/bin/python
# flamoni@juniper.net
import multiprocessing as mp
from multiprocessing import Pool
import json
import lib.script2 as script2lib
import os

def run_script2(hostname):

    result = script2lib.script2(hostname)
    if result['success'] == 0:
        with open('./logs/failed.log', 'a+') as fp:
            fp.writelines(hostname + " - " + result['message'] + "\n")
            print("FAILED: " + hostname + "  -  " + result['message'])
    else:
        with open('./logs/success.log', 'a+') as fp:
            fp.writelines(hostname + "\n")
            print("SUCCESS: " + hostname)


def run_on_all_hosts(hosts):
    pool = Pool(processes=mp.cpu_count())
    pool.map(run_script2, hosts)


# clear logs
if os.path.exists("./logs/failed.log"):
    os.remove('./logs/failed.log')
if os.path.exists("./logs/success.log"):
    os.remove('./logs/success.log')
run_on_all_hosts(filter(None, open('./config/hosts.txt').read().splitlines()))