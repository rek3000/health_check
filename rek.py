#!/bin/env python
import os, sys
import shutil, glob, re
import io 
import zipfile, tarfile
import json
import argparse
import rektools

##### DEFAULT PATHS #####
## INTERGRATED LIGHT OUT MANAGEMENT
FAULT='/fma/@usr@local@bin@fmadm_faulty.out'
TEMP='/ilom/@usr@local@bin@collect_properties.out'
FIRMWARE='/ilom/@usr@local@bin@collect_properties.out'
##
## ORACLE LINUX
IMAGE_LINUX=''
PARTITION_LINUX='/disks/df-kl.out'
RAID='' 
NETWORK='/sysconfig/ifconfig-a.out'
CPU_ULTILIZATION=''
CPU_LOAD_LINUX=''
MEM_LINUX=''
SWAP_SOL=''
EXTRACT_LOCATION='./temp/'
#HugePages = HugePages_Total * 2 /1024 = ~ 67.8% physical Memory
##
## ORACLE SOLARIS
IMAGE_SOL='/etc/release'
PARTITION_SOL='/disks/df-kl.out'
RAID_SOL='/disks/zfs/zpool_status_-v.out' 
NETWORK_SOL='/netinfo/ipadm.out'
CPU_ULTILIZATION_SOL='/sysconfig/vmstat_3_3.out'
CPU_LOAD_SOL='/sysconfig/prstat-L.out'
VCPU_SOL='/ldom/ldm_list.out'
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
            return -1

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
        return rektools.rm_ext(file, compress)
    elif compress == 'tar.gz':
        untar(file)
        return rektools.rm_ext(file, compress)
    else: return -1

# Find return the file with serial number 
def get_file(serial, compress):
    root = './sample/'
    regex = '*[_.]' + serial + '[_.]*.' + compress

    files = glob.glob(os.path.join(root, regex))
    if len(files) == 0:
        print('No file found matched with the serial list!')
        return -1
    elif len(files) == 1:
        return files[0]
    else:
        for i in range(len(files)):
            print('[', i, '] ', files[i], sep='')
        c = int(input('Which file?\n [0] '))
        return files[c]

# NO MORE SUBPROCESS MORON
def grep(path, regex, single_line=True):
    result = ''
    flag = re.MULTILINE
    pattern = re.compile(regex, flag)
    file = cat(path, False)
    content = file.readlines()

    if single_line:
        for line in range(len(content)):
            if re.search(pattern, content[line]):
                result += content[line].lstrip()
                print(line + 1, ': ', content[line], sep='', end='')
                break 
    else:
        for line in range(len(content)):
            if re.search(pattern, content[line]):
                result += content[line].lstrip()
                print(line + 1, ': ', content[line], sep='', end='')
    print()
    return result

def get_ilom(path):
    print('##### ILOM #####')
    fault = cat(path + FAULT).strip()

    inlet_temp = grep(path + TEMP, 'inlet_temp').strip().split()
    inlet_temp = ' '.join(inlet_temp[2:5])

    exhaust_temp = grep(path + TEMP, 'exhaust_temp').strip().split()
    exhaust_temp = ' '.join(exhaust_temp[2:5])

    firmware = grep(path + FIRMWARE, 'Version').strip().split()
    firmware = ' '.join(firmware[1:])

    print('##### END OF ILOM #####')
    return {'fault': fault, 'inlet': inlet_temp, 'exhaust': exhaust_temp, 'firmware': firmware} 

def get_os(path, os='SOL'):
    x = {}
    if os == 'SOL':
        image = grep(path + IMAGE_SOL, 'Solaris').strip().split()
        image = image[2]
        x['image'] = image

        vol = grep(path + PARTITION_SOL, "\\B\/\\B").strip().split()
        vol = vol[-2]
        vol_avail = 100 - int(vol[:-1])
        x['vol_avail'] = vol_avail

        raid = grep(path + RAID_SOL, "mirror").strip().split()
        if 'ONLINE' in raid:
            raid_stat = True 
        else:
            raid_stat = False
        x['raid_stat'] = raid_stat

        net_ipmp = grep(path + NETWORK_SOL, 'ipmp')
        net_aggr = grep(path + NETWORK_SOL, 'aggr')
        if not net_ipmp and not net_aggr:
            bonding = 'none'
        elif net_ipmp and not net_aggr:
            bonding = 'ipmp'
        elif net_aggr and not net_ipmp:
            bonding = 'aggr'
        else:
            bonding = 'both'
        x['bonding'] = bonding

        cpu_util = cat(path + CPU_ULTILIZATION_SOL).strip().split('\n')
        cpu_util = cpu_util[2]
        cpu_util = cpu_util.split()[21]
        cpu_util = 100 - int(cpu_util)
        x['cpu_util'] = cpu_util

        x['load'] = {}
        load = grep(path + CPU_LOAD_SOL, 'load average').strip().split(', ')
        load_avg = ' '.join(load).split()[-3:]
        load_avg = float((max(load_avg)))
        vcpu = grep(path + VCPU_SOL, 'primary').strip().split()[4]
        load_avg_per = load_avg / float(vcpu)
        load_avg_per = float(f'{load_avg_per:.3f}')
        x['load']['load_avg'] = load_avg
        x['load']['vcpu'] = vcpu
        x['load']['load_avg_per'] = load_avg_per

        mem = grep(path + MEM_SOL, 'freelist', False).strip().split()
        mem_free = mem[-1]
        mem_util = 100 - int(mem_free[:-1])
        x['mem_util'] = mem_util

        swap = cat(path + SWAP_SOL).strip().split()
        swap = [swap[8], swap[10]]
        swap[0] = int(swap[0][:-2])
        swap[1] = int(swap[1][:-2])
        swap_util = swap[0] / (swap[0] + swap[1])
        swap_util = int(swap_util * 100)
        x['swap_util'] = swap_util

        print(x)
        print()
    return x

def get_content(path):
    root = './temp/'
    org_path = path[0]
    print(org_path)
    for i in range(0, len(path)):
        path[i] = root + str(path[i])

    # @@
    ilom = get_ilom(path[0])
    os_info = get_os(path[1], 'SOL')
    name = org_path.split('_')[0]

    content = {}
    content[name] = {
            'fault': ilom['fault'],
            'inlet': ilom['inlet'],
            'exhaust': ilom['exhaust'],
            'firmware': ilom['firmware'],
            'image': os_info['image'],
            'vol_avail': os_info['vol_avail'],
            'raid_stat': os_info['raid_stat'],
            'bonding': os_info['bonding'],
            'cpu_util': os_info['cpu_util'],
            'load': os_info['load'],
            'mem_util': os_info['mem_util'],
            'swap_util': os_info['swap_util'],
    }
    print('##### NODE INFORMATION #####')
    print(json.dumps(content, indent = 2))
    print('##### END OF NODE INFORMATION #####\n')
    return content

def cat(path, stdout=True):
    result = ''
    try:
        with open(path, 'r') as file:
            content = file.readlines()
            if stdout:
                count = 0
                for l in content:
                    result += l.lstrip()
                    print(++count + 1, ': ', l, sep='', end='')
                return result
            else: 
                for l in content:
                    result += l.lstrip()
                return io.StringIO(result)
    except Exception as err:
        raise RuntimeError('Cannot open file to read') from err
        return -1

def unzip(file):
    if not zipfile.is_zipfile(file):
        print('Error: Not a zip file')
        return -1
    try:
        with zipfile.ZipFile(file, 'r') as z_object:
            z_object.extractall(path='./temp/')
            print('> UNZIP:', file)
    except Exception as err:
        print('Error:' , err)
        return -1

def untar(file):
    if not tarfile.is_tarfile(file):
        print('Error: Not a tar file')
        return -1
    try:
        with tarfile.open(file, 'r:*') as t_object:
            t_object.extractall(path='./temp/', numeric_owner=True)
            print('> UNTAR:', file)
    except Exception as err:
        print('Error:' , err)
        return -1

def extract_info():
    try:
        with open('./input', 'r') as file:
            number = file.readlines()
    except Exception as err:
        print(err)
        return -1

    output_files = []
    for i in range(len(number)):
        serial = number[i].strip()
        print(serial)
        serial = serial.split(' ')
        if len(serial) != 2: 
            print('Error: Not enough serial!')
            return -1

        path = ['','']
        print('##### EXTRACT FILES #####')
        path[0] = extract_file(serial[0], 'zip')
        path[1] = extract_file(serial[1], 'tar.gz')
        print('##### END EXTRACTION #####\n')

        if path == [-1, -1]: 
            print('Error: PATH not exist!')
            return -1

        print('PATH: ', path)

        data = input('Output file: ').strip()
        output_files += [data]

        data = './output/' + data + '.json'
        content = get_content(path)
        if rektools.save_json(data, content) == -1:
            return -1 
    return output_files

# MAIN 
def run():
    output_files = extract_info()
    if output_files == -1:
        print('Error: No files to join!')
        return -1
    choice = input('Join all input?[y/n] ')
    if choice in ['', 'yes', 'y', 'Y', 'yeah', 'YES']:
        rektools.join_json(output_files)
##### END_IMPLEMENTATION #####

##### MAIN #####
def main():
    if run() == -1: 
        clean_up_force()
        return -1
    clean_up()
    return 0

if __name__ == "__main__":
    main()
##### END_MAIN #####
