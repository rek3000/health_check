#!/bin/env python
import os, sys, subprocess
import shutil, glob, re
import json
import io 
import zipfile, tarfile
import argparse

##### DEFAULT PATHS #####
## ORACLE LINUX
FAULT_LINUX='/fma/@usr@local@bin@fmadm_faulty.out'
TEMP_LINUX='/ilom/@usr@local@bin@collect_properties.out'
FIRMWARE_LINUX='/ilom/@usr@local@bin@collect_properties.out'
IMAGE_LINUX=''
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
        print(file_path)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def clean_up():
    print('Remove unzip files? (y/n) ', end='')
    choice = input()
    if choice in ['', 'yes', 'y', 'Y', 'yeah', 'YES']:
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

#get a dictionary as input and dump it to a json type file
def save_json(file, content):
    if not content:
        return -1
    with open(file, 'w') as file:
        json.dump(content, file, indent=2)

def read_json(file):
    with open(file, 'r+') as f:
        content = json.load(f)
    return content

#sucks
def join_json(output):
    z = {}
    with open('./output/data.json', 'a+') as file:
        for i in output:
            z[i] = {}
            path = './output/' + i + '.json'
            buffer = read_json(path)
            z[i].update(buffer)
        json.dump(z, file, indent=4)

# NO MORE SUBPROCESS MORON
def grep(path, regex, uniq=True):
    result = ''
    flag = re.MULTILINE
    pattern = re.compile(regex, flag)
    file = cat(path, False)
    content = file.readlines()
    if uniq:
        for line in range(0, len(content)):
            if re.search(pattern, content[line]):
                result += content[line].lstrip()
                print(line + 1, ': ', content[line], sep='', end='')
                break # STOP after find first match
    else:
        for line in range(0, len(content)):
            if re.search(pattern, content[line]):
                result += content[line].lstrip()
                print(line + 1, ': ', content[line], sep='', end='')
    print()
    return result

def get_content(path):
    root = './temp/'
    org_path = path
    name = path[0].split('_')[0]
    for i in range(0, len(path)):
        path[i] = root + str(path[i])

    # @@ SUCKS 
    fault = cat(path[0] + FAULT_SOL).strip()

    inlet_temp = grep(path[0] + TEMP_SOL, 'inlet_temp')
    inlet_temp = subprocess.run(["awk" ,"{print $3, $4, $5}"], input=inlet_temp, stdout=subprocess.PIPE, text=True).stdout.strip()

    exhaust_temp = grep(path[0] + TEMP_SOL, 'exhaust_temp')
    exhaust_temp = subprocess.run(["awk" ,"{print $3, $4, $5}"], input=exhaust_temp, stdout=subprocess.PIPE, text=True).stdout.strip()

    firmware = grep(path[0] + FIRMWARE_SOL, 'Version')
    firmware = subprocess.run(["awk" ,"{print $2, $3}"], input=firmware, stdout=subprocess.PIPE, text=True).stdout.strip()

    image = grep(path[1] + IMAGE_SOL, 'Solaris')
    image = subprocess.run(["awk" ,"{print $3}"], input=image, stdout=subprocess.PIPE, text=True).stdout.strip()

    partition = grep(path[1] + PARTITION_SOL, "\\B\/\\B")
    partition = subprocess.run(["awk" ,"{print $5}"], input=partition, stdout=subprocess.PIPE, text=True).stdout
    partition = str(100 - int(partition[:-2])) + '%'

    net_ipmp = grep(path[1] + NETWORK_SOL, 'ipmp')
    net_aggr = grep(path[1] + NETWORK_SOL, 'aggr')
    if  not net_ipmp and not net_aggr:
        net = 'none'
    elif net_ipmp and not net_aggr:
        net = 'ipmp'
    elif net_aggr and not net_ipmp:
        net = 'aggr'
    else:
        net = 'both'
    # net = net

    cpu_util = cat(path[1] + CPU_ULTILIZATION_SOL).strip()
    cpu_util = subprocess.run(["sed","3!d"], input=cpu_util,  stdout=subprocess.PIPE, text=True).stdout
    cpu_util = subprocess.run(["awk", "{print $22}"], input=cpu_util, stdout=subprocess.PIPE, text=True).stdout
    cpu_util = str(100 - int(cpu_util)) + '%'

    load = grep(path[1] + CPU_LOAD_SOL, 'load average')
    load = subprocess.run(["awk" ,"{print $8, $9, $10}"], input=load, stdout=subprocess.PIPE, text=True).stdout
    load = load.split(',') 
    load = str(max(load))

    mem = grep(path[1] + MEM_SOL, 'freelist', False)
    mem = subprocess.run(["awk", "{print $5}"], input=mem, stdout=subprocess.PIPE, text=True).stdout
    free_mem = str(100 - int(mem[:-2])) + '%'

    swap = cat(path[1] + SWAP_SOL)
    swap = subprocess.run(["awk", "-F", ' ', "{print $9, $11}"], input=swap, stdout=subprocess.PIPE, text=True).stdout
    swap = swap.split()
    swap[0] = int(swap[0][:-2])
    swap[1] = int(swap[1][:-2])
    free_swap = swap[1] / (swap[0] + swap[1])
    free_swap = str(int(free_swap * 100)) + '%'

    # content = fault+inlet_temp+exhaust_temp+firmware+image+partition+net+cpu_util+load+free_mem+free_swap
    content = {
            'fault': fault,
            'inlet': inlet_temp,
            'exhaust': exhaust_temp,
            'firmware': firmware,
            'image': image,
            'partition': partition,
            'net': net,
            'cpu_util': cpu_util,
            'load': load,
            'free_mem': free_mem,
            'free_swap': free_swap,
    }

    print(content)
    return content

def cat(path, stdout=True):
    result = ''
    with open(path, 'r') as file:
        content = file.readlines()
        if stdout:
            for l in range(0, len(content)):
                result += content[l].lstrip()
                print(l + 1, ': ', content[l], sep='', end='')
            return result
        else: 
            for l in range(0, len(content)):
                result += content[l].lstrip()
            return io.StringIO(result)

def unzip(file):
    if not zipfile.is_zipfile(file):
            return -1
    with zipfile.ZipFile(file, 'r') as z_object:
        z_object.extractall(path='./temp/')

def untar(file):
    if not tarfile.is_tarfile(file):
        return -1
    with tarfile.open(file, 'r:*') as t_object:
        t_object.extractall(path='./temp/', numeric_owner=True)

def save_file(file, content):
    with open(file, 'w') as file:
        file.write(content)

def rm_ext(file, compress):
    return file.split('/')[2][:-len(compress)-1]

def run():
    # number = int(input('Enter number of servers: '))
    with open('./input', 'r') as file:
        number = file.readlines()
    output = []
    for i in range(0, len(number)):
        serial = number[i].strip()
        print(serial)
    #     serial = ''
    #     print('Server [', i, ']', sep='')
    #     serial = input('Enter serial numbers [ilom & explorer]: ')
        serial = serial.split(' ')
        if len(serial) != 2: return -1

        path = ['','']
        path[0] = extract_file(serial[0], 'zip')
        path[1] = extract_file(serial[1], 'tar.gz')

        if path == [-1, -1]: return -1

        print('PATH: ', path)

        data = input('Output file: ').strip()
        print(data)
        output += [data]

        data = './output/' + data + '.json'
        content = get_content(path)
        save_json(data, content)
    choice = input('Join all input?[y/n] ')
    print(output)
    if choice in ['', 'yes', 'y', 'Y', 'yeah', 'YES']:
        join_json(output)

    # out = read_json(data)
    # print(json.dumps(out, indent=2))
    # save_file('output.txt', content)
##### END_IMPLEMENTATION #####

##### MAIN #####
def main():
    if run() == -1: return -1
    clean_up()

if __name__ == "__main__":
    main()
##### END_MAIN #####
