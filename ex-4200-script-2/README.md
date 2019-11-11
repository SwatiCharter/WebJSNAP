config/credentials.txt - Two-line file that contains the super-user username on first line, password on second line

config/hosts.txt - Contains new-line-delimited list of hostnames/IP addresses (preferably hostnames, as this file is where things like log file outputs from this script get their name from)

config/root_password.txt - Single-line file that contains the actual root password. We need this because an "su root" must be ran by the script to mount the / directory to read-write and then mount it back to read-only

logs - This directory contains information about what steps were taken on the device, failures, etc...

-----------------

Multi execution example (hostnames are read from ./config/hosts.txt):
python master.py