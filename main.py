#!/bin/env python
import os, sys
import shutil, glob
import json
import zipfile, tarfile
import argparse

##### DEFAULT PATHS #####
## ORACLE LINUX
FAULT_LINUX='/fma/@usr@local@bin@fmadm_faulty.out'
TEMP_LINUX='/ilom/@usr@local@bin@collect_properties.out'
FIRMWARE_LINUX='/ilom/@usr@local@bin@collect_properties.out'
IMAGE_LINUX='' # Solaris
PARTITION_LINUX='/disks/df-kl.out'
RAID='' 
NETWORK='/sysconfig/ifconfig-a.out'
CPU_ULTILIZATION=''
CPU_LOAD_LINUX=''
MEM_LINUX=''
SWAP_SOL=''
EXTRACT_LOCATION='./temp/'
##
## ORACLE SOLARIS
FAULT_SOL='/fma/@usr@local@bin@fmadm_faulty.out'
TEMP_SOL='/ilom/@usr@local@bin@collect_properties.out'
FIRMWARE_SOL='/ilom/@usr@local@bin@collect_properties.out'
IMAGE_SOL='/etc/release'
PARTITION_SOL='/disks/df-kl.out'
RAID='' 
NETWORK_SOL='/netinfo/ipadm.out'
CPU_ULTILIZATION_SOL='/sysconfig/vmstat_3_3.out'
CPU_LOAD_SOL='/sysconfig/prstat-L.out'
MEM_SOL='/disks/zfs/mdb/mdb-memstat.out'
SWAP_SOL='/disks/swap-s.out'
##
##### END_PATHS #####

##### IMPLEMETATION #####
def clean_files():
    folder = './temp/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
            os.unlink('./output.txt')
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

def clean_up():
    print('Remove unzip files? (y/n) ', end='')
    choice = input('')
    if choice in ['yes', 'y', 'Y', 'yeah', 'YES']:
        clean_files()

def clean_up_force():
    print('FORCE CLEAN UP DUE TO ERROR!')
    clean_files()

def check_valid(path):
    return os.path.isdir(path)

def extract_file(serial, compress):
    compress = compress.lower()
    file = get_file(serial, compress) 
    if file == -1: return -1
    print('Extracting: ', file)
    if compress == 'zip':
        unzip(file)
        return rm_ext(file, compress)
    elif compress == 'tar.gz':
        untar(file)
        return rm_ext(file, compress)
    else: return -1

# Find return the file with serial number 
def get_file(serial, compress):
    #works for now
    root = './sample/'
    regex = '*[_.]' + serial + '[_.]*.' + compress

    files = glob.glob(os.path.join(root, regex))
    print(files)
    if len(files) == 1:
        return files[0]
    elif len(files) > 1:
        i = 0
        for file in files:
            print('[',i,'] ', file, sep='')
            i += 1
        choice = int(input('Which file?\n [0] '))
        return files[choice]
    else: return -1

def get_content(path):
    root = './temp/'
    for i in range(0, len(path)):
        path[i] = root + path[i]

    # path[0] = ILOM | path[1] = EXPLORER
    fault = print_file(path[0] + FAULT_SOL)
    temp = grep(path[0] + TEMP_SOL, '_temp')
    firmware = grep(path[0] + FIRMWARE_SOL, 'Version')
    # image = print_file(path[1] + IMAGE_SOL)
    image = grep(path[1] + IMAGE_SOL, 'Solaris')
    partition = print_file(path[1] + PARTITION_SOL) 
    net = print_file(path[1] + NETWORK_SOL)
    cpu_util = print_file(path[1] + CPU_ULTILIZATION_SOL)
    load = grep(path[1] + CPU_LOAD_SOL, 'load average')
    mem = print_file(path[1] + MEM_SOL)
    swap = print_file(path[1] + SWAP_SOL)
    content = fault+temp+firmware+image+partition+net+cpu_util+load+mem+swap
    return content

def grep(path, word):
    result = ''
    with open(path, 'r') as file:
        content = file.readlines()
        count = 0
        for line in range(0, len(content)):
            if count == 2: break
            if content[line].find(word) != -1:
                count = count + 1 
                result += content[line].lstrip()
                print(line + 1, ': ', content[line], sep='', end='')
    print()
    return result + '\n'
            
def print_file(path):
    result = ''
    with open(path, 'r') as file:
        content = file.readlines()
        count = 0
        for line in range(0, len(content)):
            result += content[line].lstrip()
            print(line + 1, ': ', content[line], sep='', end='')
    print()
    return result + '\n'

def unzip(file):
    if not zipfile.is_zipfile(file):
            return -1
    with zipfile.ZipFile(file, 'r') as z_object:
        z_object.extractall(path='./temp/')

def untar(file):
    if not tarfile.is_tarfile(file):
        return -1
    with tarfile.open(file, 'r:*') as t_object:
        # t_object.extractall(path='./temp/', numeric_owner=True)
        t_object.extractall(path='./temp/')

def save_file(file, content):
    with open(file, 'w') as file:
        file.write(content)

def rm_ext(file, compress):
    return file.split('/')[2][:-len(compress)-1]

def run():
    # parser = argparse.ArgumentParser(description='Process system log files to a output file.')
    # parser.add_argument('type', help='Enter the type of log')
    # args = parser.parse_args()
    # if args == 'solaris':
        serial = input('Enter serial numbers [ilom & explorer]: ')
        serial = serial.split(' ')
        if len(serial) != 2: return -1

        path = ['','']
        path[0] = extract_file(serial[0], 'zip')
        path[1] = extract_file(serial[1], 'tar.gz') ### Quick test 
        if path == [-1, -1]: return -1

    # if sys.argv[0] == '-z':
    #     extract_file('*', 'tar.gz'

        print('PATH: ', path)
        if path == -1: 
            clear_up_force()
            return -1 

        content = get_content(path)
        save_file('output.txt', content)
##### END_IMPLEMENTATION #####

##### MAIN #####
def main():
    if run() == -1: return -1
    clean_up()

if __name__ == "__main__":
    main()
##### END_MAIN #####
