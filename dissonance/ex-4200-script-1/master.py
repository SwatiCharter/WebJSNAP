#!/opt/junosvenv/bin/python
# Importing multiprocessing as a whole isn't really necessary since we ended up changing the "processes" argument to
# a static 10, but I left this in for historical purposes
import multiprocessing as mp
# Import Pool from multiprocessing, which allows us multi-threading
from multiprocessing import Pool
# Import our rc_uploader.py module so we can feed the function into multiprocessing
import lib.rc_uploader as rc_uploader
# Import os module so we can delete log files upon execution
import os

# This function gets executed in multiple threads
def run_rc_uploader(hostname):

    result = rc_uploader.upload_rc(hostname)

    if result['success'] == 0:
        with open('./logs/failed.log', 'a+') as fp:
            fp.writelines(hostname + " - " + result['message'] + "\n")
            print("FAILED: " + hostname + " - " + result['message'])
    else:
        with open('./logs/success.log', 'a+') as fp:
            fp.writelines(hostname + "\n")
            print("SUCCESS: " + hostname)


# This function's only purpose is to create a thread pool and feed it a function (run_rc_uploader()) and a list of hostnames
def run_on_all_hosts(hosts):
    pool = Pool(processes=mp.cpu_count())
    pool.map(run_rc_uploader, hosts)


# Clears our result log files if they exist already. This means that the failed.log and success.log contents only reflect the latest master.py execution
if os.path.exists("./logs/failed.log"):
    os.remove('./logs/failed.log')
if os.path.exists("./logs/success.log"):
    os.remove('./logs/success.log')
    
# Actually trigger our multiprocessing execution of run_rc_uploader()
run_on_all_hosts(filter(None, open('./config/hosts.txt').read().splitlines()))