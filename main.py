import os
import json

def check_valid(path):
    return os.path.isdir(path)

def get_content(path):
    content = ''
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

##### MAIN #####
def main():
    # error handling
    path=input('Enter path to log folder(ILOM): ')
    if not check_valid('./' + path):
        print('Invalid path')
        return

    fault = print_file(path + '/fma/@usr@local@bin@fmadm_faulty.out')
    temp = grep(path + '/ilom/@usr@local@bin@collect_properties.out', '_temp')
    firmware = grep(path + '/ilom/@usr@local@bin@spshexec_version.out', 'SP firmware')

    if fault.strip() == 'No faults found':
        fault = ''
    temp = temp.split()
        
    firmware = 'Phiên bản ILOM hiện tại: ' + firmware.split()[2] + '\n'
    temp = 'Nhiệt độ vào: ' + temp[2] + ' ' + temp[3] + ' ' + temp[4]+ '\n' + 'Nhiệt độ ra: ' + temp[7] + ' ' + temp[8] + ' ' + temp[9] + ' ' + '\n'
    content = fault+temp+firmware
    # content = get_content(path)
    
    save_file('output.txt', content)
    
if __name__ == "__main__":
    main()
