#!/bin/env python
import os
import shutil
import glob
import json
# from zipfile import ZipFile
import zipfile


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
FAULT='/fma/@usr@local@bin@fmadm_faulty.out'
TEMP='/ilom/@usr@local@bin@collect_properties.out'
FIRMWARE='/ilom/@usr@local@bin@collect_properties.out'
IMAGE=''
PARTITION=''
NETWORK=''
CPU_ULTILIZATION=''
CPU_LOAD=''
MEMORY=''
SWAP=''

EXTRACT_LOCATION=''
####

##### IMPLEMETATION #####
def extract_file(serial):
    file = get_file(serial) 
    if not file: return
    print(file)

    if zipfile.is_zipfile(file) is True:
        print('Valid ZIP file')
    else:
        return -1
    
    with zipfile.ZipFile(file, 'r') as z_object:
        z_object.extractall(path='./temp/')
    z_object.close()

def get_file(serial):
    regex = "sample/*" + serial + "*.zip"
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
        return False

def check_valid(path):
    return os.path.isdir(path)

def get_content():
    path = input('Enter path to log folder(ILOM): ')

    # error handling
    if not check_valid('./' + path):
        print('Invalid path')
        return

    fault = print_file(path + FAULT)
    temp = grep(path + TEMP, '_temp')
    firmware = grep(path + FIRMWARE, 'SP firmware')
    content = fault+temp+firmware
    return content

def grep(path, word):
    result = ""
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
    
def run():
    # content = get_content()
    # save_file('output.txt', content)

    serial = input('Enter serial number: ')
    extract_file(serial)


##### MAIN #####
def main():
    run()
    clean_up()

    # if fault.strip() == 'No faults found':
    #     fault = 'Không có lỗi\n'
    # temp = temp.split()
    # firmware = 'Phiên bản ILOM hiện tại: ' + firmware.split()[0] + '\n'
    # temp = 'Nhiệt độ vào: ' + temp[2] + ' độ ' + temp[4] + '\n' + 'Nhiệt độ ra: ' + temp[7] + ' độ ' + temp[9] + ' ' + '\n'
    
if __name__ == "__main__":
    main()
