##!/bin/env python
# 
# DOCUMENT FILE FROM LOG FILES GENERATOR
#
import os, sys, signal, io
import shutil, glob
import json
import zipfile, tarfile
import argparse
from rekdoc import doc
from rekdoc import tools
from rekdoc.const import *

##### DECORATORS #####
def debug(func):
    def _debug(*args, **kwargs):
        result = func(*args, **kwargs)
        print(
            f"{func.__name__}(args: {args}, kwargs: {kwargs}) -> {result}"
        )
        return result
    return _debug
##### END OF DECORATORS #####

##### IMPLEMETATION #####
def clean_files(folder='./temp/'):
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

def clean_up(path='./temp/', prompt='Remove files? (y/n) '):
    choice = input(prompt)
    if choice in ['', 'yes', 'y', 'Y', 'yeah', 'YES']:
        clean_files(path)
        return
    return -1 

def clean_up_force(path='./temp/'):
    print('FORCE CLEAN UP DUE TO ERROR!')
    clean_files(path)
    return -1

def check_valid(path):
    return os.path.isdir(path)

def drw_ilom(path, out_dir):
    fault = io.StringIO()
    fault.write(path + FAULT + '\n')
    fault.write(tools.cat(path + FAULT))
    tools.drw_text_image(fault, out_dir + 'fault.png')

    temp = io.StringIO()
    temp.write(path + TEMP + '\n')
    reg = '^ /System/Cooling$'
    temp.write(tools.cursed_grep(path + TEMP, reg, 8).getvalue())
    tools.drw_text_image(temp, out_dir + 'temp.png')

    firmware = io.StringIO()
    firmware.write(path + FIRMWARE + '\n')
    reg = '^Oracle'
    firmware.write(tools.cursed_grep(path + FIRMWARE, reg, 5).getvalue())
    tools.drw_text_image(firmware, out_dir + 'firmware.png')
    return ['fault.png', 'temp.png', 'firmware.png']

def drw_os(path, out_dir):
    image = io.StringIO()
    image.write(path + IMAGE_SOL + '\n')
    image.write(tools.cat(path + IMAGE_SOL))
    tools.drw_text_image(image, out_dir + 'image.png')

    vol = io.StringIO()
    vol.write(path + PARTITION_SOL + '\n')
    vol.write(tools.cat(path + PARTITION_SOL))
    tools.drw_text_image(vol, out_dir + 'vol.png')

    raid = io.StringIO()
    raid.write(path + RAID_SOL + '\n')
    raid.write(tools.cat(path + RAID_SOL))
    tools.drw_text_image(raid, out_dir + 'raid.png')

    net = io.StringIO()
    net.write(path + NETWORK_SOL + '\n')
    net.write(tools.cat(path + NETWORK_SOL))
    tools.drw_text_image(net, out_dir + 'net.png')

    cpu_idle = io.StringIO()
    cpu_idle.write(path + CPU_ULTILIZATION_SOL + '\n')
    cpu_idle.write(tools.cat(path + CPU_ULTILIZATION_SOL))
    tools.drw_text_image(cpu_idle, out_dir + 'cpu_idle.png')

    load = io.StringIO()
    load.write(path + CPU_LOAD_SOL + '\n')
    load.write(tools.cat(path + CPU_LOAD_SOL))
    tools.drw_text_image(load, out_dir + 'load.png')

    mem = io.StringIO()
    mem.write(path + MEM_SOL + '\n')
    mem.write(tools.cat(path + MEM_SOL))
    tools.drw_text_image(mem, out_dir + 'mem.png')

    swap = io.StringIO()
    swap.write(path + SWAP_SOL + '\n')
    swap.write(tools.cat(path + SWAP_SOL))
    tools.drw_text_image(swap, out_dir + 'swap.png')
    return ['image.png', ['vol.png', 'raid.png'], 'net.png', 'cpu_idle.png', 'load.png', 'mem.png', 'swap.png']

def drw_content(path, output):
    ilom = drw_ilom(path[0], output)
    os_info = drw_os(path[1], output)
    images = ilom + os_info
    return images

def extract_file(serial, compress):
    compress = compress.lower()
    regex = '*' + serial + '*.' + compress
    file = get_file(regex, root='./sample/') 
    if file == -1: return -1

    if compress == 'zip':
        unzip(file)
        return tools.rm_ext(file, compress)
    elif compress == 'tar.gz':
        untar(file)
        return tools.rm_ext(file, compress)
    else: return -1

# Find return the file with serial number 
def get_file(regex, root=''):
    path = root + regex
    files = glob.glob(path, recursive=True)
    if len(files) == 0:
        print('No file found matched!')
        return -1
    elif len(files) == 1:
        return files[0]
    else:
        for i in range(len(files)):
            print('[', i, '] ', files[i], sep='')
        c = ''
        while True:
            try:
                c = int(input('Which file?\n [0] ') or '0')
                if c < 0 and c > len(files):
                    continue
            except KeyboardInterrupt:
                print()
                sys.exit()
            except ValueError:
                continue
            break
        return files[c]

def get_ilom(path):
    print('##### ILOM #####')
    fault = tools.cat(path + FAULT).strip()

    inlet_temp = tools.grep(path + TEMP, 'inlet_temp').strip().split()
    inlet_temp = ' '.join(inlet_temp[2:5])

    exhaust_temp = tools.grep(path + TEMP, 'exhaust_temp').strip().split()
    exhaust_temp = ' '.join(exhaust_temp[2:5])

    firmware = tools.grep(path + FIRMWARE, 'Version').strip().split()
    firmware = ' '.join(firmware[1:])

    print('##### END OF ILOM #####')
    return {'fault': fault, 'inlet': inlet_temp, 'exhaust': exhaust_temp, 'firmware': firmware} 

def get_os(path, os='SOL'):
    x = {}
    if os == 'SOL':
        image = tools.grep(path + IMAGE_SOL, 'Solaris').strip().split()
        image = image[2]
        x['image'] = image

        vol = tools.grep(path + PARTITION_SOL, "\\B\/\\B").strip().split()
        vol = vol[-2]
        vol_avail = 100 - int(vol[:-1])
        x['vol_avail'] = vol_avail

        raid = tools.grep(path + RAID_SOL, "mirror").strip().split()
        if 'ONLINE' in raid:
            raid_stat = True 
        else:
            raid_stat = False
        x['raid_stat'] = raid_stat

        net_ipmp = tools.grep(path + NETWORK_SOL, 'ipmp')
        net_aggr = tools.grep(path + NETWORK_SOL, 'aggr')
        if not net_ipmp and not net_aggr:
            bonding = 'none'
        elif net_ipmp and not net_aggr:
            bonding = 'ipmp'
        elif net_aggr and not net_ipmp:
            bonding = 'aggr'
        else:
            bonding = 'both'
        x['bonding'] = bonding

        cpu_idle = tools.cat(path + CPU_ULTILIZATION_SOL).strip().split('\n')
        cpu_idle = cpu_idle[2]
        cpu_idle = cpu_idle.split()[21]
        cpu_util = 100 - int(cpu_idle)
        x['cpu_util'] = cpu_util

        x['load'] = {}
        load = tools.grep(path + CPU_LOAD_SOL, 'load average').strip().split(', ')
        load_avg = ' '.join(load).split()[-3:]
        load_avg = float((max(load_avg)))
        vcpu = tools.grep(path + VCPU_SOL, 'primary').strip().split()[4]
        vcpu = int(vcpu)
        load_avg_per = load_avg / vcpu
        load_avg_per = float(f'{load_avg_per:.3f}')
        x['load']['load_avg'] = load_avg
        x['load']['vcpu'] = vcpu
        x['load']['load_avg_per'] = load_avg_per

        mem = tools.grep(path + MEM_SOL, 'freelist', False).strip().split()
        mem_free = mem[-1]
        mem_util = 100 - int(mem_free[:-1])
        x['mem_util'] = mem_util

        swap = tools.cat(path + SWAP_SOL).strip().split()
        swap = [swap[8], swap[10]]
        swap[0] = int(swap[0][:-2])
        swap[1] = int(swap[1][:-2])
        swap_util = swap[0] / (swap[0] + swap[1])
        swap_util = int(swap_util * 100)
        x['swap_util'] = swap_util

        # print(x)
        print()
    return x

def get_content(node, path):
    # @@
    ilom = get_ilom(path[0])
    os_info = get_os(path[1], 'SOL')
    name = node

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

def unzip(file):
    if not zipfile.is_zipfile(file):
        print('Error: Not a zip file')
        return -1
    try:
        with zipfile.ZipFile(file, 'r') as zip:
            zip.extractall(path='./temp/')
    except Exception as err:
        print('Error:' , err)
        return -1

def untar(file):
    # sucks
    if not tarfile.is_tarfile(file):
        print('Error: Not a tar file')
        return -1
    print(file)
    try:
        with tarfile.open(file, 'r:gz') as tar:
            try:
                tar.extractall(path='./temp/', numeric_owner=True)
            except IOError as err:
                clean_files('./temp/' + tools.rm_ext(file, 'tar.gz'))
                tar.extractall(path='./temp/', numeric_owner=True)
    except IOError as err:
        print(err)
        return -1

def compile(nodes):
    n = len(nodes)
    content_files = []
    for i in range(n):
        path = ['','']
        print('##### EXTRACT FILES #####')
        path[0] = extract_file(nodes[i], 'zip')
        path[1] = extract_file(nodes[i], 'tar.gz')
        print('##### END EXTRACTION #####\n')

        if path == [-1, -1]: 
            print('Error: file not exist!')
            return -1
        print('PATH: ', path)

        # node = path[1].split('.')[2] # get machine name
        node = nodes[i]
        content_files += [node]
        try: 
            os.mkdir('output/' + node)
            print('Folder created: ' + node)
        except FileExistsError as err:
            print('Output folder exist!')
            clean_up(path='./output/' + node, prompt='Do you want to replace it? [y/n] ')
            # os.mkdir('output/' + node)

        file_name = node
        print(path)
        root = './temp/'
        for i in range(0, len(path)):
            path[i] = root + str(path[i])
        print(path)
        content = get_content(node, path)
        # DRAW IMAGES FOR CONTENT
        images = drw_content(path, 'output/' + node + '/')
        # END DRAWING
        if tools.save_json('output/' + node + '/' + node, content) == -1:
            return -1 
        if tools.save_json('output/' + node + '/images', images) == -1:
            return -1 
    return content_files 

# FLOW OF PROGRAM
def run(nodes, output):
    content_files = compile(nodes)
    if content_files == -1:
        print('Error: No files to join!')
        return -1

    choice = input('Join all input?[y/n] ')
    if choice in ['', 'yes', 'y', 'Y', 'yeah', 'YES']:
        tools.join_json(content_files, output)

    choice = input('GENERATE DOCUMENT?[y/n] ')
    if choice in ['', 'yes', 'y', 'Y', 'yeah', 'YES']:
        doc.run(output)
##### END_IMPLEMENTATION #####

##### MAIN #####
def main():
    parser = argparse.ArgumentParser(prog='rek', description='Fetch, process data from ILOM and Explorer log files then write them to a report file.',
                                     usage='%(prog)s [options] node [node...] [-o] file',
                                     epilog='Created by Rek',
                                     exit_on_error=False)
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('-i', help='file with node names',
                        # nargs='',
                        metavar='file'
                        )
    parser.add_argument('node', help='machine names',
                        nargs='*', 
                        default=None,
                        )
    parser.add_argument('-o', help='output file name',
                        metavar='doc',
                        default='output/example',
                        )
                       
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", required=False, action="store_true")
    group.add_argument("-q", "--quiet", required=False, action="store_true")
    args = parser.parse_args()

    if (not args.node) and (not args.i):
        parser.parse_args(['-h'])
        return 
    nodes_input = []
    try:
        with open(args.i, 'r') as f:
            line = f.readlines()
            for i in range(len(line)):
                nodes_input.append(line[i].strip())
    except Exception as err:
        print('Invalid or missing input file')

    nodes = nodes_input + args.node
    print(nodes)

    if run(nodes, args.o) == -1: 
        clean_up_force()
        return -1
    clean_up()
    sys.exit()

if __name__ == "__main__":
    main()
##### END_MAIN #####
