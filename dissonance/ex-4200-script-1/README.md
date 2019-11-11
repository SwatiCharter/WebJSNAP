credentials.txt - Two-line file that contains the super-user username on first line, password on second line

hosts.txt - Contains new-line-delimited list of hostnames/IP addresses (preferably hostnames, as this file is where things like log file outputs from this script get their name from)

logs - This directory contains information about what steps were taken on the device, failures, etc...

root_password.txt - Contains the root password. We need to su root to mount /

-----------------

Multi execution example (hostnames are read from ./config/hosts.txt):
python master.py