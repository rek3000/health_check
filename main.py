#!/bin/env python
import os
import shutil
import glob
import json
import zipfile
import tarfile

checklist = [
        [1, "Kiểm tra nhiệt độ", ""],
        [2, "Kiểm tra phiên bản ILOM firmware", ""],
        [3, "Kiểm tra trạng thái phần cứng", ""],
        [4, "Kiểm tra phiên bản Image", ""],
        [5, "Kiểm tra cấu hình RAID và dung lượng phân vùng OS", ""],
        [6, "Kiểm tra cấu hình network", ""],
        [7, "Kiểm tra CPU Utilization", ""],
        [8, "Kiểm tra Flash IO", ""],
        [9, "Kiểm tra Flash Bandwidth", ""],
        [10, "Kiểm tra Hard Disk IO", ""],
        [11, "Kiểm tra Hard Disk Bandwidth", ""],
    ]

#### PATH 
## ORACLE SOLARIS
FAULT='/fma/@usr@local@bin@fmadm_faulty.out'
TEMP='/ilom/@usr@local@bin@collect_properties.out'
FIRMWARE='/ilom/@usr@local@bin@collect_properties.out'
IMAGE='/patch+pkg/pkg_list-af_entire.out' # Solaris
PARTITION='/disks/df-kl.out'
RAID='' 
NETWORK='/sysconfig/ifconfig-a.out'
CPU_ULTILIZATION=''
CPU_LOAD=''
MEMORY=''
SWAP=''
EXTRACT_LOCATION='./temp/'
#TODO ## ORACLE LINUX
# FAULT='/fma/@usr@local@bin@fmadm_faulty.out'
# TEMP='/ilom/@usr@local@bin@collect_properties.out'
# FIRMWARE='/ilom/@usr@local@bin@collect_properties.out'
# IMAGE='/patch+pkg/pkg_list-af_entire.out' # Solaris
# PARTITION='/disks/df-kl.out'
# RAID='' 
# NETWORK='sysconfig/ifconfig-a.out'
# CPU_ULTILIZATION=''
# CPU_LOAD=''
# MEMORY=''
# SWAP=''
####

##### IMPLEMETATION #####
def clean_up():
    folder = './temp/'
    print('Remove unzip files? (y/n) ', end='')
    choice = input('')
    if choice in ['yes', 'y', 'Y', 'yeah', 'YES']:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def check_valid(path):
    return os.path.isdir(path)

def extract_file(serial, compress):
    compress = compress.lower()
    file = get_file(serial, compress) 
    if file == -1: return -1
    print(file)

    #This sucks, fix later
    if compress == 'zip':
        if zipfile.is_zipfile(file) is False:
            return -1
        with zipfile.ZipFile(file, 'r') as z_object:
            z_object.extractall(path='./temp/')
        z_object.close()

        # return the file name without extension
        return file.split('/')[1][:-len(compress)-1]

    elif compress == 'tar.gz':
        if tarfile.is_tarfile(file) is False:
            return -1
        with tarfile.open(file, 'r:*') as t_object:
            t_object.extractall(path='./temp/', numeric_owner=True)
        t_object.close()

        # return the file name without extension
        return file.split('/')[1][:-len(compress)-1] 
    else: 
        return -1

def get_file(serial, compress):
    # This sucks too, works for now
    regex = "sample/*" + serial + "*." + compress
    files = glob.glob(regex)
    if len(files) == 1:
        return files[0]
    elif len(files) > 1:
        i = 0
        for file in files:
            print(i,':', file)
            i += 1
        choice = int(input('Which file? [n] '))
        return files[choice]
    else:
        return -1

def get_content(path):
    fault = print_file(path + FAULT)
    temp = grep(path + TEMP, '_temp')
    firmware = grep(path + FIRMWARE, 'SP firmware')
    image = print_file(path + IMAGE)
    partition = print_file(path + PARTITION) 
    content = fault+temp+firmware+image+partition
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

def save_file(file, content):
    with open(file, 'w') as file:
        file.write(content)

def run():
    # serial = input('Enter serial number: ')
    # path = extract_file(serial, 'zip')
    serial2 = input('Enter serial number (2): ')
    path = extract_file(serial2, 'tar.gz') ### Quick test 
    print('PATH: ', path)
    if path == -1: 
        return -1 

    # content = get_content('./temp/' + path)
    # save_file('output.txt', content)

##### MAIN #####
def main():
    if run() == -1:
        clean_up()
        return -1
    clean_up()

if __name__ == "__main__":
    main()
