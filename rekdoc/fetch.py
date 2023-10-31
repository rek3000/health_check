##!/bin/env python
# 
# DOCUMENT FILE FROM LOG FILES GENERATOR
#
import os, sys, signal, io
import shutil, glob
import json
import zipfile, tarfile
# import argparse
import click
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
def clean_files(folder='temp/'):
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

def clean_up(path='temp/', prompt='Remove files? (y/n) ', force=False):
    if force:
        clean_files(path)
    else:
        choice = input(prompt)
        if choice in ['', 'yes', 'y', 'Y', 'yeah', 'YES']:
            clean_files(path)
        return

def clean_up_force(path='temp/'):
    print('FORCE CLEAN UP DUE TO ERROR!')
    clean_files(path)
    return -1

def check_valid(path):
    return os.path.isdir(path)

def drw_ilom(path, out_dir, verbose=False):
    fault = io.StringIO()
    fault.write(path + FAULT + '\n')
    fault.write(tools.cat(os.path.normpath(path + FAULT), verbose=verbose))
    tools.drw_text_image(fault, os.path.normpath(out_dir + '/fault.png'))

    temp = io.StringIO()
    temp.write(path + TEMP + '\n')
    reg = '^ /System/Cooling$'
    temp.write(tools.cursed_grep(os.path.normpath(path + TEMP), reg, 8, verbose=verbose).getvalue())
    tools.drw_text_image(temp, os.path.normpath(out_dir + '/temp.png'))

    firmware = io.StringIO()
    firmware.write(path + FIRMWARE + '\n')
    reg = '^Oracle'
    firmware.write(tools.cursed_grep(os.path.normpath(path + FIRMWARE), reg, 5, verbose=verbose).getvalue())
    tools.drw_text_image(firmware, os.path.normpath(out_dir + '/firmware.png'))
    return ['fault.png', 'temp.png', 'firmware.png']

def drw_os(path, out_dir, verbose=False):
    image = io.StringIO()
    image.write(path + IMAGE_SOL + '\n')
    image.write(tools.cat(os.path.normpath(path + IMAGE_SOL), verbose=verbose))
    tools.drw_text_image(image, os.path.normpath(out_dir + '/image.png'))

    vol = io.StringIO()
    vol.write(path + PARTITION_SOL + '\n')
    vol.write(tools.cat(os.path.normpath(path + PARTITION_SOL), verbose=verbose))
    tools.drw_text_image(vol, os.path.normpath(out_dir + '/vol.png'))

    raid = io.StringIO()
    raid.write(path + RAID_SOL + '\n')
    raid.write(tools.cat(os.path.normpath(path + RAID_SOL), verbose=verbose))
    tools.drw_text_image(raid, os.path.normpath(out_dir + '/raid.png'))

    net = io.StringIO()
    net.write(path + NETWORK_SOL + '\n')
    net.write(tools.cat(os.path.normpath(path + NETWORK_SOL), verbose=verbose))
    tools.drw_text_image(net, os.path.normpath(out_dir + '/net.png'))

    cpu_idle = io.StringIO()
    cpu_idle.write(path + CPU_ULTILIZATION_SOL + '\n')
    cpu_idle.write(tools.cat(os.path.normpath(path + CPU_ULTILIZATION_SOL), verbose=verbose))
    tools.drw_text_image(cpu_idle, os.path.normpath(out_dir + '/cpu_idle.png'))

    load = io.StringIO()
    load.write(path + CPU_LOAD_SOL + '\n')
    load.write(tools.cat(os.path.normpath(path + CPU_LOAD_SOL), verbose=verbose))
    tools.drw_text_image(load, os.path.normpath(out_dir + '/load.png'))

    mem = io.StringIO()
    mem.write(path + MEM_SOL + '\n')
    mem.write(tools.cat(os.path.normpath(path + MEM_SOL), verbose=verbose))
    tools.drw_text_image(mem, os.path.normpath(out_dir + '/mem.png'))

    swap = io.StringIO()
    swap.write(path + SWAP_SOL + '\n')
    swap.write(tools.cat(os.path.normpath(path + SWAP_SOL), verbose=verbose))
    tools.drw_text_image(swap, os.path.normpath(out_dir + '/swap.png'))
    return ['image.png', ['vol.png', 'raid.png'], 'net.png', 'cpu_idle.png', 'load.png', 'mem.png', 'swap.png']

def drw_content(path, output, verbose=False):
    ilom = drw_ilom(path[0], output, verbose=False)
    os_info = drw_os(path[1], output, verbose=False)
    images = ilom + os_info
    return images

def extract_file(serial, compress, verbose, force):
    compress = compress.lower()
    regex = '*' + serial + '*.' + compress
    file = get_file(regex, root='sample/') 
    if file == -1: return -1

    if compress == 'zip':
        unzip(file, verbose, force)
        dir =  tools.rm_ext(file, compress)
        path = os.path.split(dir)[1]
        return path
    elif compress == 'tar.gz':
        untar(file, verbose, force)
        dir =  tools.rm_ext(file, compress)
        path = os.path.split(dir)[1]
        return path
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

def get_ilom(path, verbose):
    fault = tools.cat(os.path.normpath(path + FAULT), verbose=verbose).strip()

    inlet_temp = tools.grep(os.path.normpath(path + TEMP), 'inlet_temp', verbose=verbose).strip().split()
    inlet_temp = ' '.join(inlet_temp[2:5])

    exhaust_temp = tools.grep(os.path.normpath(path + TEMP), 'exhaust_temp', verbose=verbose).strip().split()
    exhaust_temp = ' '.join(exhaust_temp[2:5])

    firmware = tools.grep(os.path.normpath(path + FIRMWARE), 'Version', verbose=verbose).strip().split()
    firmware = ' '.join(firmware[1:])

    return {'fault': fault, 'inlet': inlet_temp, 'exhaust': exhaust_temp, 'firmware': firmware} 

def get_os(path, os_name='SOL', verbose=False):
    x = {}
    if os_name == 'SOL':
        image = tools.grep(os.path.normpath(path + IMAGE_SOL), 'Solaris', verbose=verbose).strip().split()
        image = image[2]
        x['image'] = image

        vol = tools.grep(os.path.normpath(path + PARTITION_SOL), "\\B\/\\B", verbose=verbose).strip().split()
        vol = vol[-2]
        vol_avail = 100 - int(vol[:-1])
        x['vol_avail'] = vol_avail

        raid = tools.grep(os.path.normpath(path + RAID_SOL), "mirror", verbose=verbose).strip().split()
        if 'ONLINE' in raid:
            raid_stat = True 
        else:
            raid_stat = False
        x['raid_stat'] = raid_stat

        net_ipmp = tools.grep(os.path.normpath(path + NETWORK_SOL), 'ipmp', verbose=verbose)
        net_aggr = tools.grep(os.path.normpath(path + NETWORK_SOL), 'aggr', verbose=verbose)
        if not net_ipmp and not net_aggr:
            bonding = 'none'
        elif net_ipmp and not net_aggr:
            bonding = 'ipmp'
        elif net_aggr and not net_ipmp:
            bonding = 'aggr'
        else:
            bonding = 'both'
        x['bonding'] = bonding

        cpu_idle = tools.cat(os.path.normpath(path + CPU_ULTILIZATION_SOL), verbose=verbose).strip().split('\n')
        cpu_idle = cpu_idle[2]
        cpu_idle = cpu_idle.split()[21]
        cpu_util = 100 - int(cpu_idle)
        x['cpu_util'] = cpu_util

        x['load'] = {}
        load = tools.grep(os.path.normpath(path + CPU_LOAD_SOL), 'load average', verbose=verbose).strip().split(', ')
        load_avg = ' '.join(load).split()[-3:]
        load_avg = float((max(load_avg)))
        vcpu = tools.grep(os.path.normpath(path + VCPU_SOL), 'primary', verbose=verbose).strip().split()[4]
        vcpu = int(vcpu)
        load_avg_per = load_avg / vcpu
        load_avg_per = float(f'{load_avg_per:.3f}')
        x['load']['load_avg'] = load_avg
        x['load']['vcpu'] = vcpu
        x['load']['load_avg_per'] = load_avg_per

        mem = tools.grep(os.path.normpath(path + MEM_SOL), 'freelist', False, verbose=verbose).strip().split()
        mem_free = mem[-1]
        mem_util = 100 - int(mem_free[:-1])
        x['mem_util'] = mem_util

        swap = tools.cat(os.path.normpath(path + SWAP_SOL), verbose=verbose).strip().split()
        swap = [swap[8], swap[10]]
        swap[0] = int(swap[0][:-2])
        swap[1] = int(swap[1][:-2])
        swap_util = swap[0] / (swap[0] + swap[1])
        swap_util = int(swap_util * 100)
        x['swap_util'] = swap_util

    return x

def get_content(node, path, verbose):
    # @@
    ilom = get_ilom(path[0], verbose)
    os_info = get_os(path[1], 'SOL', verbose)
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
    if verbose:
        print(json.dumps(content, indent = 2))
    return content

def unzip(file, verbose, force):
    if not zipfile.is_zipfile(file):
        print('Error: Not a zip file')
        return -1
    if verbose:
        print('Extracting: ' + file)
    try:
        with zipfile.ZipFile(file, 'r') as zip:
            try:
                zip.extractall(path='temp/')
            except IOError as err:
                clean_up(os.path.normpath('temp/' + os.path.split(tools.rm_ext(file, 'zip'))[1]), force=force)
                zip.extractall(path='temp/')
    except IOError as err:
        print(err)
        return -1

def untar(file, verbose, force):
    if not tarfile.is_tarfile(file):
        print('Error: Not a tar file')
        return -1
    if verbose:
        print('Extracting: ' + file)
    try:
        with tarfile.open(file, 'r:gz') as tar:
            try:
                tar.extractall(path='temp/', numeric_owner=True)
            except IOError as err:
                clean_up(os.path.normpath('temp/' + os.path.split(tools.rm_ext(file, 'tar.gz'))[1]), force=force)
                tar.extractall(path='temp/', numeric_owner=True)
    except IOError as err:
        print(err)
        return -1

def compile(nodes, verbose, force):
    n = len(nodes)
    content_files = []
    for i in range(n):
        path = ['','']
        path[0] = extract_file(nodes[i], 'zip', verbose, force)
        path[1] = extract_file(nodes[i], 'tar.gz', verbose, force)

        if path == [-1, -1]: 
            print('Error: file not exist!')
            return -1
        if verbose:
            print('EXTRACTED FILES: ', path)

        # node = path[1].split('.')[2] # get machine name
        node = nodes[i]
        content_files += [node]
        try: 
            os.mkdir(os.path.normpath('output/' + node))
            print('Folder created: ' + node)
        except FileExistsError as err:
            print('Output folder exist!')
            clean_up(path=os.path.normpath('output/' + node), prompt='Do you want to replace it? [y/n] ', force=force)

        file_name = node
        root = 'temp/'
        for i in range(0, len(path)):
            path[i] = os.path.normpath(root + str(path[i]))
        # print(path)
        content = get_content(node, path, verbose)
        # DRAW IMAGES FOR CONTENT
        images = drw_content(path, os.path.normpath('output/' + node + '/'), verbose=verbose)
        # END DRAWING
        if tools.save_json(os.path.normpath('output/' + node + '/' + node + '.json'), content) == -1:
            return -1 
        if tools.save_json(os.path.normpath('output/' + node + '/images.json'), images) == -1:
            return -1 
    return content_files 

# FLOW OF PROGRAM
def run(nodes, output, verbose, force):
    content_files = compile(nodes, verbose, force)
    if content_files == -1:
        print('Error: No files to join!')
        return -1
    tools.join_json(content_files, output)
##### END_IMPLEMENTATION #####

##### MAIN #####
@click.group()
def main():
    click.echo('duh')
    pass

if __name__ == "__main__":
    main()
##### END_MAIN #####
