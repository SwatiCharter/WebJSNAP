#!/opt/junosvenv/bin/python
# flamoni@juniper.net
from jnpr.junos.device import Device
from jnpr.junos.utils.start_shell import StartShell
import sys, os, json
import time

# Custom logging function to log to a file specific to a hostname, and print the information
def log(hostname, msg):
    timestamp = time.ctime()

    with open('./logs/' + hostname, 'a+') as fp:
        print(hostname + ' - ' + timestamp + ' - ' + msg)
        fp.write(hostname + ' - ' + timestamp + ' - ' + msg + '\n')

# This function will be called later on after we've rebooted the device. It essentially just attempts to connect to the
# given device a certain number of times before it finally gives up and returns False. The number of times it attempts
# to connect is based on the "900" we see below and the "timeout=10" value in the Device() creation.
def attemptToConnectToRebootedDevice(hostname, username, password):
    timeout_counter = 0
    while True:
        try:
            timeout_counter += 10
            dev = Device(host=hostname, user=username, passwd=password, timeout=10)
            dev.open()
            return dev
        except:
            if timeout_counter > 900:
                return False

# The actual bread and butter function that does everything. I, ideally, would've liked to split this up, as it's far
# too big of a function, but time constraints, plus it was "easier" to read because the whole MOP was relatively
# procedural
def script2(hostname):
    ######### Prologue stuff

    # Remove old log file if one exists for the given hostname
    if os.path.exists('./logs/'+hostname):
        os.remove('./logs/'+hostname)

    # Start a new log file
    log(hostname, "------------------------")

    # Variables we'll use in different places. Same quick method for assigning username and password in one line
    (username, password) = open('./config/credentials.txt').read().splitlines()[:2]
    root_password = open('./config/root_password.txt').readline()
    rc_file_location = '/etc/rc.mount.platform'
    rc_md5 = 'e4e17e0aa795f4dd790ed3f15f18859b'


    # Can't use context managers here since we're rebooting
    # Attempt to connect to the given hostname
    try:
        dev = Device(host=hostname, user=username, passwd=password)
        dev.open()
    except Exception as e:
        log(hostname, 'Failed to connect for Device()')
        return {'success': 0, 'message': 'Failed to connect to Device()'}

    # Attempt to create a shell connection to the given hostname
    try:
        shell = StartShell(dev)
        shell.open()
    except:
        log(hostname, 'Failed to connect for StartShell()')
        return {'success': 0, 'message': 'Failed to connect to StartShell()'}

    # RC file check - We do this using Junos's RPC for "file list" op command, this is exactly
    # like sending "file list /etc/rc.mount.platform" from the command-line
    file_show = dev.rpc.file_list(path=rc_file_location)
    file_show = file_show.xpath('//total-files')

    # If the length of file_show variable is 0, that means the file wasn't found
    if len(file_show) < 1:
        return {'success': 0, 'message': 'RC file not found in /etc/rc.mount.platform, didn\'t show in ls listing'}

    file_show = str(file_show[0].text).strip()

    log(hostname, 'file_show: ' + file_show)

    # Excessive check most likely, but I wanted to be certain. Pretty much the same check as the previous check
    if file_show != "1":
        return {'success': 0, 'message': 'RC file not found in /etc/rc.mount.platform'}
    ############################################

    # MD5 file check - We do this using Junos's RPC for "file checksum md5"
    md5_rc_check = dev.rpc.get_checksum_information(path=rc_file_location)
    md5_rc_check = md5_rc_check.xpath('//checksum')

    # If the length of md5_rc_check is less than 0, that means no checksum XML node was found, which means something
    # went wrong, or that the file didn't exist. Realistically we probably don't need this here because execution would
    # not make it this far due to our previous checks, but I wanted to be explicit about the checks we're doing and
    # follow the MOP as exact as I could
    if len(md5_rc_check) < 1:
        return {'success': 0, 'message': 'MD5 check on RC file unable to be executed'}

    md5_rc_check = str(md5_rc_check[0].text).strip()

    # Log / print information about the step we're on so the user is aware of where the script is currently at in its
    # execution
    log(hostname, 'md5 of rc file: ' + md5_rc_check + ' compared to: ' + rc_md5)

    # If the checksum doesn't match our hard-coded/expected checksum of the file, we report a failure back to master.py
    # in the form of a dict
    if md5_rc_check != rc_md5:
        return {'success': 0, 'message': 'MD5 check FAILED. RC on device is corrupted, did not match ' + rc_md5}

    ############################################

    # Switch StartShell with su root - We need this to run some of the commands later on. StartShell() is an
    # "extension" for PyEZ that allows us simple access to shell

    shell.run('su root', this='Password:', timeout=5)
    shell.run(root_password)

    # Same whoami check we did in script 1
    whoami = shell.run('whoami')
    if 'whoami\r\r\nroot\r\n' not in whoami[1]:
        log(hostname, 'INVALID ROOT PASSWORD GIVEN, COULD NOT SU TO ROOT. EXITING.')
        return {'success': 0, 'message': 'Invalid root password given. Exiting.'}



    # c. Run fsck utility on the Unmounted partition to make sure its clean

    # Check which is backup partition (/dev/da0s1a or /dev/da0s2a) using "show system snapshot media internal" RPC
    show_system_snapshot = dev.rpc.get_snapshot_information(media='internal')
    snapshot_information = show_system_snapshot.xpath('//snapshot-information')

    if len(snapshot_information) < 1:
        return {'success': 0, 'message': 'Unable to retrieve "show system snapshot media internal" output'}

    snapshot_information = snapshot_information[0]

    snapshot_medium = snapshot_information.xpath('//snapshot-medium')

    partitions = {}

    for medium in snapshot_medium:
        temp = str(medium.text).split('internal (')[1]
        if 'primary' in temp:
            temp = temp.split(') (primary)')[0]
            partitions['primary'] = temp
        else:
            temp = temp.split(') (backup)')[0]
            partitions['backup'] = temp

    log(hostname, 'partitions: ' + json.dumps(partitions))

    fsck_output = shell.run('fsck -f -y ' + partitions['backup'])
    log(hostname, "fsck -f -y " + partitions['backup'] + "\n" + fsck_output[1])


    # d. Perform snapshot slice alternate and save rescue configuration

    ########## Save rescue configuration - request system configuration rescue save
    log(hostname, "request configuration rescue save - Starting")
    request_rescue_configuration_save = dev.rpc.request_save_rescue_configuration(dev_timeout=500)
    log(hostname, "request configuration rescue save - Completed")
    #@TODO: Not sure if there's error-handling we need to do here. There is a //success xpath we can check for


    log(hostname, "request system snapshot slice alternate - Starting")
    request_system_snapshot_slice_alternate = dev.rpc.request_snapshot(slice="alternate", dev_timeout=500)
    log(hostname, "request system snapshot slice alternate - Completed")





    ########### REBOOT THE DEVICE
    request_system_reboot = dev.rpc.request_reboot()
    log(hostname, "REBOOTING - Initializing sleep to give device time to actually reboot")

    # Need to kill the dev and shell connections or it'll error out.
    # Need to sleep to give device time to reboot. Junos waits 60 seconds before initiating shutdown process, so
    #  I pad 30 seconds on to give it time to actually shutdown.
    shell.close()
    dev.close()
    time.sleep(90)

    # While loop to reconnect to rebooted device, attemptToConnectToRebootedDevice() returns a Device() instantiation
    log(hostname, "Beginning post-reboot reconnect attempts")
    reconnDev = attemptToConnectToRebootedDevice(hostname, username, password)

    # this means we timed out... device needs manual intervention
    if reconnDev == False:
        log(hostname, "Post-reboot FAILED. Device failed to come back up - Manual intervention required")
        return {'success': 0, 'message': "Post-reboot FAILED. Device failed to come back up - Manual intervention required"}

    log(hostname, "Post-reboot reconnection successful!")

    log(hostname, "Checking if we booted from backup partition - show system storage partitions")

    # Check if backup partition was booted
    partition_check = reconnDev.rpc.get_system_storage_partitions()
    partition_check = partition_check.xpath('//partitions/booted-from')

    if len(partition_check) > 1:
        return {'success': 0,
                'message': "Couldn't determine active/backup partition from 'show system storage partitions'"}

    partition_check = str(partition_check[0].text).strip()

    log(hostname, 'show system storage partitions: booted from ' + partition_check)

    ################################################################################
    ################################################################################
    ################################################################################
    ################################################################################

    # If we booted from backup, COMMENCE THE "OTHER" SCRIPT (MOP-Clean-Primary-partition.pdf).
    # I should probably extract this out into a separate function, but I don't want to deal with figuring out what
    # variables I need to pass-thru
    if partition_check == "backup":

        ########### Check which is backup partition (/dev/da0s1a or /dev/da0s2a)
        show_system_snapshot = reconnDev.rpc.get_snapshot_information(media='internal')
        snapshot_information = show_system_snapshot.xpath('//snapshot-information')

        if len(snapshot_information) < 1:
            return {'success': 0, 'message': 'Unable to retrieve "show system snapshot media internal" output'}

        snapshot_information = snapshot_information[0]

        snapshot_medium = snapshot_information.xpath('//snapshot-medium')

        partitions = {}

        for medium in snapshot_medium:
            temp = str(medium.text).split('internal (')[1]
            if 'primary' in temp:
                temp = temp.split(') (primary)')[0]
                partitions['primary'] = temp
            else:
                temp = temp.split(') (backup)')[0]
                partitions['backup'] = temp

        log(hostname, 'partitions: ' + json.dumps(partitions))

        fsck_output = shell.run('fsck -f -y ' + partitions['backup'])
        log(hostname, "fsck -f -y " + partitions['backup'] + "\n" + fsck_output[1])

        # 3. Take a snapshot to the alternate partition (this is a hidden command), then compare "show system snapshot media internal" to ensure
        #     both partitions have the same versions
        log(hostname, 'request system snapshot media internal slice alternate - Starting')
        request_system_snapshot_media_internal_slice_alternate = reconnDev.rpc.request_snapshot(slice='alternate', media='internal', dev_timeout=500)
        log(hostname, 'request system snapshot media internal slice alternate - Completed')



        # 3a. Packages should be the same on both slices
        log(hostname, 'show system snapshot media internal - Started')

        show_system_snapshot_media_internal = reconnDev.rpc.get_snapshot_information(media='internal')
        show_system_snapshot_media_internal = show_system_snapshot_media_internal.xpath('//software-version')
        log(hostname, 'show system snapshot media internal - Comparing packages between slices')

        software_versions = {}
        for software_index, software_version in enumerate(show_system_snapshot_media_internal):
            packages = software_version.xpath('./package')
            software_versions.setdefault(software_index, {})
            for package_index, package in enumerate(packages):
                package_name = str(package.xpath('./package-name')[0].text).strip()
                package_version = str(package.xpath('./package-version')[0].text).strip()

                software_versions[software_index][package_name] = package_version

        packages_match = True
        for package_name in software_versions[0].keys():
            if software_versions[0][package_name] != software_versions[1][package_name]:
                packages_match = False
                break

        if packages_match != True:
            log(hostname, "Packages from 'show system snapshot media internal' do not match")
            return {'success': 0, 'message': "Packages from 'show system snapshot media internal' do not match"}

        log(hostname, 'show system snapshot media internal - Comparison completed')


        #######################

        # 4. show system storage partitions - The MOP doesn't really explain what we're looking for with this command. Skipping for now.


        # 5. show system alarms - Check for alarm-description containing "Boot from backup root", if we find one, run "request system reboot slice alternate media internal"

        show_system_alarms = reconnDev.rpc.get_system_alarm_information()
        show_system_alarms = show_system_alarms.xpath('//alarm-description')

        for alarm_description in show_system_alarms:
            alarm_description = str(alarm_description.text).strip()
            # If we see the backup root alarm, we need to reboot AGAIN
            if "Boot from backup root" in alarm_description:
                log(hostname, 'REBOOTING - Backup root alarm FOUND - request system reboot slice alternate media internal')

                reconnDev.rpc.request_reboot(media='internal', slice='alternate')

                reconnDev.close()
                time.sleep(90)

                # While loop to reconnect to rebooted device, attemptToConnectToRebootedDevice() returns a Device instantation
                log(hostname, "Beginning second post-reboot reconnect attempts")
                secondReconnDev = attemptToConnectToRebootedDevice(hostname, username, password)

                # this means we timed out... device needs manual intervention
                if secondReconnDev == False:
                    log(hostname, "SECOND Post-reboot FAILED. Device failed to come back up - Manual intervention required")
                    return {'success': 0,
                            'message': "SECOND Post-reboot FAILED. Device failed to come back up - Manual intervention required"}

                log(hostname, "Second post-reboot reconnection successful!")

                log(hostname, "Checking if we booted from backup partition - show system storage partitions")

                # Check if backup partition was booted
                partition_check = secondReconnDev.rpc.get_system_storage_partitions()
                partition_check = partition_check.xpath('//partitions/booted-from')

                if len(partition_check) > 1:
                    return {'success': 0,
                            'message': "Couldn't determine active/backup partition from 'show system storage partitions'"}

                partition_check = str(partition_check[0].text).strip()

                if partition_check == "backup":
                    log(hostname, "PROCEDURE FAILED, DEVICE STILL BOOTING FROM BACKUP PARTITION, DEVICE NEEDS TO BE RMA'D")
                    return {'success': 0,
                            'message': "PROCEDURE FAILED, DEVICE STILL BOOTING FROM BACKUP PARTITION, DEVICE NEEDS TO BE RMA'D"}







    # 3. Run the NAND media check after boot up
    with StartShell(reconnDev) as reconnShell:
        reconnShell.run('su root', this='Password:', timeout=5)
        reconnShell.run(root_password)

        nand_mediack = reconnShell.run('nand-mediack -C')
        log(hostname, 'Running nand-mediack -C')
        if "nand-mediack -C\r\r\nMedia check on da0 on ex platforms\r\nroot@" not in nand_mediack[1]:
            log(hostname, 'nand-mediack check FAILED: ' + nand_mediack[1])
            return {'success': 0, 'message': 'nand-mediack check FAILED'}
        else:
            log(hostname, 'nand-mediack check PASSED: ' + nand_mediack[1])

    reconnDev.close()


    log(hostname, "Completed execution")
    log(hostname, "------------------------")
    return {'success': 1, 'message': 'SCRIPT COMPLETED EXECUTION'}
    ############################################



if __name__ == "__main__":
    # Main
    def main():
        if len(sys.argv) <= 1:
            print ("Hostname required")
            exit()

        hostname = sys.argv[1]

        print(json.dumps(script2(hostname)))

    main()