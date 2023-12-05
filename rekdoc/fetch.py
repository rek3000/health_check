##!/bin/env python
#
# DOCUMENT FILE FROM LOG FILES GENERATOR
#

__version__ = "1.0"
__author__ = "Rek"

# Standard Library
import os
import io
import sys
import shutil
import glob
import json
import zipfile
import tarfile
import logging

# Local library
from rekdoc import tools
from rekdoc.const import *


##### DECORATORS #####
def debug(func):
    def _debug(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__}(args: {args}, kwargs: {kwargs}) -> {result}")
        return result

    return _debug


##### END OF DECORATORS #####


##### IMPLEMETATION #####
# TODO: REWRITE for Windows compatibility
def clean_files(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        logging.info("Deleted: " + file_path)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))
            return -1


def clean_up(path, prompt="Remove files?", force=False):
    if force:
        clean_files(path)
    else:
        print(prompt + "[y/n]", end='')
        choice = input() or "\n"

        if choice in ["\n", "y", "yes"]:
            clean_files(path)
        return


def clean_up_force(path):
    print("FORCE CLEAN UP DUE TO ERROR!")
    clean_files(path)
    return -1


def check_valid(path):
    return os.path.isdir(path)


##### IMAGE PROCESSING #####
## DRAW ILOM ##
def drw_fault(path, out_dir):
    fault = io.StringIO()
    fault.write(path + FAULT + "\n")
    stdout = tools.cat(os.path.normpath(path + FAULT))
    fault.write(str(stdout))
    tools.drw_text_image(fault, os.path.normpath(out_dir + "/fault.png"))


def drw_temp(path, out_dir):
    temp = io.StringIO()
    temp.write(path + TEMP + "\n")
    reg = "^ /System/Cooling$"
    stdout = tools.grep(os.path.normpath(path + TEMP), reg, False, 9)
    for line in stdout:
        temp.write(str(line) + "\n")
    tools.drw_text_image(temp, os.path.normpath(out_dir + "/temp.png"))


def drw_firmware(path, out_dir):
    firmware = io.StringIO()
    firmware.write(path + FIRMWARE + "\n")
    reg = "^Oracle"
    stdout = tools.grep(os.path.normpath(path + FIRMWARE), reg, True, 5)
    firmware.write(str(stdout))
    tools.drw_text_image(firmware, os.path.normpath(out_dir + "/firmware.png"))


def drw_ilom(path, out_dir):
    drw_fault(path, out_dir)
    drw_temp(path, out_dir)
    drw_firmware(path, out_dir)

    return ["fault.png", "temp.png", "firmware.png"]


## END DRAW ILOM ##


## DRAW OF ##
def drw_image(path, out_dir):
    image = io.StringIO()
    image.write(path + IMAGE_SOL + "\n")
    image.write(tools.cat(os.path.normpath(path + IMAGE_SOL)))
    tools.drw_text_image(image, os.path.normpath(out_dir + "/image.png"))
    return image


def drw_vol(path, out_dir):
    vol = io.StringIO()
    vol.write(path + PARTITION_SOL + "\n")
    vol.write(tools.cat(os.path.normpath(path + PARTITION_SOL)))
    tools.drw_text_image(vol, os.path.normpath(out_dir + "/vol.png"))
    return vol


def drw_raid(path, out_dir):
    raid = io.StringIO()
    raid.write(path + RAID_SOL + "\n")
    raid.write(tools.cat(os.path.normpath(path + RAID_SOL)))
    tools.drw_text_image(raid, os.path.normpath(out_dir + "/raid.png"))
    return raid


def drw_net(path, out_dir):
    net = io.StringIO()
    net.write(path + NETWORK_SOL + "\n")
    net.write(tools.cat(os.path.normpath(path + NETWORK_SOL)))
    tools.drw_text_image(net, os.path.normpath(out_dir + "/net.png"))
    return net


def drw_cpu(path, out_dir):
    cpu_idle = io.StringIO()
    cpu_idle.write(path + CPU_ULTILIZATION_SOL + "\n")
    cpu_idle.write(tools.cat(os.path.normpath(path + CPU_ULTILIZATION_SOL)))
    tools.drw_text_image(cpu_idle, os.path.normpath(out_dir + "/cpu_idle.png"))
    return cpu_idle


def drw_load(path, out_dir):
    load = io.StringIO()
    load.write(path + CPU_LOAD_SOL + "\n")
    load.write(tools.cat(os.path.normpath(path + CPU_LOAD_SOL)))
    tools.drw_text_image(load, os.path.normpath(out_dir + "/load.png"))
    return load


def drw_mem(path, out_dir):
    mem = io.StringIO()
    mem.write(path + MEM_SOL + "\n")
    mem.write(tools.cat(os.path.normpath(path + MEM_SOL)))
    tools.drw_text_image(mem, os.path.normpath(out_dir + "/mem.png"))
    return mem


def drw_swap(path, out_dir):
    swap = io.StringIO()
    swap.write(path + SWAP_SOL + "\n")
    swap.write(tools.cat(os.path.normpath(path + SWAP_SOL)))
    tools.drw_text_image(swap, os.path.normpath(out_dir + "/swap.png"))
    return swap


# SUCKS, rewrite later
def drw_os(path, out_dir):
    drw_image(path, out_dir)
    drw_vol(path, out_dir)
    drw_raid(path, out_dir)
    drw_net(path, out_dir)
    drw_cpu(path, out_dir)
    drw_load(path, out_dir)
    drw_mem(path, out_dir)
    drw_swap(path, out_dir)
    return [
        "image.png",
        ["vol.png", "raid.png"],
        "net.png",
        "cpu_idle.png",
        "load.png",
        "mem.png",
        "swap.png",
    ]


def drw_content(path, output):
    ilom = drw_ilom(path[0], output)
    os_info = drw_os(path[1], output)
    images = ilom + os_info
    logging.info(images)
    return images


def extract_file(serial, root, compress, force):
    compress = compress.lower()
    regex = "*" + serial + "*." + compress
    file = get_file(regex, root=root)
    if file == -1:
        return -1

    if compress == "zip":
        unzip(file, force)
        dir = tools.rm_ext(file, compress)
        path = os.path.split(dir)[1]
        return path
    elif compress == "tar.gz":
        untar(file, force)
        dir = tools.rm_ext(file, compress)
        path = os.path.split(dir)[1]
        return path
    else:
        return -1


# Find return the file with serial number
def get_file(regex, root="./sample/"):
    path = root + regex
    files = glob.glob(path, recursive=True)
    if len(files) == 0:
        raise RuntimeError("No file found matched!")
    elif len(files) == 1:
        return files[0]
    else:
        for i in range(len(files)):
            print("[", i, "] ", files[i], sep="")
        c = ""
        while True:
            try:
                c = int(input("Which file?\n [0] ") or "0")
                if c < 0 and c > len(files):
                    continue
            except KeyboardInterrupt:
                print()
                sys.exit()
            except ValueError:
                continue
            break
        return files[c]


##### FETCH ILOM ######
def get_fault(path):
    try:
        stdout = tools.grep(os.path.normpath(path + FAULT), "*", True, 9)
        fault = stdout.strip()
        return fault
    except RuntimeError:
        print("Failed to fetch fault data")
        raise


def get_temp(path):
    try:
        temps = tools.grep(
            os.path.normpath(path + TEMP), "^ /System/Cooling$", False, 9
        )
        inlet_temp = ""
        exhaust_temp = ""
        for line in temps:
            if "inlet_temp" in line:
                inlet_temp = " ".join(line.split()[2:5])
                continue
            elif "exhaust_temp" in line:
                exhaust_temp = " ".join(line.split()[2:5])
                continue
        return inlet_temp, exhaust_temp
    except RuntimeError:
        print("Failed to fetch temperature")
        raise


def get_firmware(path):
    try:
        stdout = tools.grep(os.path.normpath(path + FIRMWARE), "Version", True)
        firmware = " ".join(stdout.strip("\r\n").split()[1:])
        return firmware
    except RuntimeError:
        print("Failed to fetch firmware")
        raise


def get_ilom(path):
    try:
        fault = get_fault(path)
        inlet_temp, exhaust_temp = get_temp(path)
        firmware = get_firmware(path)
    except RuntimeError:
        print("Fetching ILOM is interrupted because of error")
        raise

    ilom = {
        "fault": fault,
        "inlet": inlet_temp,
        "exhaust": exhaust_temp,
        "firmware": firmware,
    }

    logging.debug(json.dumps(ilom, ensure_ascii=False))

    return ilom


#####


##### FETCH OS ######
def get_image(path):
    try:
        stdout = tools.grep(os.path.normpath(path + IMAGE_SOL),
                            "Solaris", True)
        image = stdout.strip().split()
        image = image[2]
        return image
    except RuntimeError:
        print("Failed to fetch image")
        raise


def get_vol(path):
    try:
        stdout = tools.grep(os.path.normpath(path + PARTITION_SOL),
                            "\\B/$", True)
        vol = stdout.strip().split()
        vol = vol[-2]
        return vol
    except RuntimeError:
        print("Failed to fetch volume")
        raise


def get_raid(path):
    try:
        stdout = tools.grep(os.path.normpath(path + RAID_SOL), "mirror", True)
        raid = stdout.strip().split()
        if "ONLINE" in raid:
            raid_stat = True
        else:
            raid_stat = False
        return raid_stat
    except RuntimeError:
        print("Failed to fetch raid")
        raise


def get_bonding(path):
    try:
        net_ipmp = tools.grep(os.path.normpath(path + NETWORK_SOL),
                              "ipmp", True)
        net_aggr = tools.grep(os.path.normpath(path + NETWORK_SOL),
                              "aggr", True)
        if not net_ipmp and not net_aggr:
            bonding = "none"
        elif net_ipmp and not net_aggr:
            bonding = "ipmp"
        elif net_aggr and not net_ipmp:
            bonding = "aggr"
        else:
            bonding = "both"
        return bonding
    except RuntimeError:
        print("Failed to fetch bonding status")
        raise


def get_cpu_util(path):
    try:
        stdout = tools.cat(os.path.normpath(path + CPU_ULTILIZATION_SOL))
        cpu_idle = stdout.strip().split("\n")
        cpu_idle = cpu_idle[2]
        cpu_idle = cpu_idle.split()[21]
        cpu_util = 100 - int(cpu_idle)
        return [cpu_idle, cpu_util]
    except RuntimeError:
        print("Failed to feth cpu util")
        raise


def get_load_avg(path):
    try:
        stdout = tools.grep(os.path.normpath(path + CPU_LOAD_SOL),
                            "load average", True)
        load = stdout.strip().split(", ")
        load_avg = " ".join(load).split()[-3:]
        load_avg = float(max(load_avg))
        return load_avg
    except RuntimeError:
        print("Failed to get load average")
        raise


def get_vcpu(path):
    try:
        stdout = tools.grep(os.path.normpath(path + VCPU_SOL),
                            "Status", single_match=False)
        vcpu = stdout[-1].split()[4]
        vcpu = int(vcpu) + 1
        return vcpu
    except RuntimeError:
        print("Failed to fetch VCPU")
        raise


def get_load(path):
    try:
        load_avg = get_load_avg(path)
        vcpu = get_vcpu(path)
        load_avg_per = load_avg / vcpu
        load_avg_per = float(f"{load_avg_per:.3f}")
        return load_avg, vcpu, load_avg_per
    except RuntimeError:
        print("Failed to fetch load")
        raise


def get_mem_util(path):
    try:
        stdout = tools.grep(os.path.normpath(path + MEM_SOL),
                            "^Free", False)
        mem = stdout[-1].split()
        mem_free = mem[-1]
        logging.debug(mem_free)
        mem_util = 100 - float(mem_free[:-1])
        return mem_free, mem_util
    except RuntimeError:
        print("Failed to fetch memory util")
        raise


def get_swap_util(path):
    try:
        stdout = tools.cat(os.path.normpath(path + SWAP_SOL))
        swap_free = stdout.strip().split()
        swap_free = [swap_free[8], swap_free[10]]
        swap_free[0] = float(swap_free[0][:-2])
        swap_free[1] = float(swap_free[1][:-2])
        swap_util = swap_free[0] / (swap_free[0] + swap_free[1])
        swap_util = float("{:.1f}".format(swap_util * 100))

        return swap_free, swap_util
    except RuntimeError:
        print("Failed to get swap util")
        raise


def get_os(path, os_name="SOL"):
    x = {}
    if os_name == "SOL":
        try:
            image = get_image(path)

            vol = get_vol(path)
            vol_avail = 100 - int(vol[:-1])
            x["image"] = image
            x["vol_avail"] = vol_avail

            raid_stat = get_raid(path)
            x["raid_stat"] = raid_stat

            bonding = get_bonding(path)
            x["bonding"] = bonding

            cpu_util = get_cpu_util(path)[1]
            x["cpu_util"] = cpu_util

            load = get_load(path)
            x["load"] = {}
            x["load"]["load_avg"] = load[0]
            x["load"]["vcpu"] = load[1]
            x["load"]["load_avg_per"] = load[2]

            mem_util = get_mem_util(path)[1]
            x["mem_util"] = mem_util

            swap_util = get_swap_util(path)[1]
            x["swap_util"] = swap_util
        except RuntimeError:
            print("Failed to fetch OS information")
            raise
    return x


##### END FETCH OS ######


##### FETCH OVERVIEW #####
def get_product(path):
    product = tools.grep(os.path.normpath(path + PRODUCT),
                         "product_name", True)
    return product


def get_serial(path):
    serial = tools.grep(os.path.normpath(path + SERIAL),
                        "serial_number", True)
    return serial


def get_ip(path):
    # ip = grep(os.path.normpath(path + NETWORK_SOL), "serial_number", True)
    pass


##### END OVERVIEW #####
def get_overview(node, path):
    pass
    name = node
    product_name = get_product(path[0])
    serial = get_serial(path[0])
    ip = get_ip(path[1])
    content = {}
    content[name] = {
        "host_name": name,
        "product_name": product_name,
        "serial": serial,
        "ip": ip,
    }

    return content


def get_detail(node, path):
    # @@
    try:
        ilom = get_ilom(path[0])
        os_info = get_os(path[1], "SOL")
    except RuntimeError:
        raise
    name = node

    content = {}
    content[name] = {
        "fault": ilom["fault"],
        "inlet": ilom["inlet"],
        "exhaust": ilom["exhaust"],
        "firmware": ilom["firmware"],
        "image": os_info["image"],
        "vol_avail": os_info["vol_avail"],
        "raid_stat": os_info["raid_stat"],
        "bonding": os_info["bonding"],
        "cpu_util": os_info["cpu_util"],
        "load": os_info["load"],
        "mem_util": os_info["mem_util"],
        "swap_util": os_info["swap_util"],
    }
    logging.info("JSON file: " + json.dumps(content,
                                            indent=2, ensure_ascii=False))
    return content


def unzip(file, force):
    if not zipfile.is_zipfile(file):
        logging.error("Error: Not a zip file")
        return -1
    logging.info("Extracting: " + file)
    try:
        with zipfile.ZipFile(file, "r") as zip:
            try:
                zip.extractall(path="temp/")
            except IOError:
                clean_up(
                    os.path.normpath(
                        "temp/" + os.path.split(tools.rm_ext(file, "zip"))[1]
                    ),
                    force=force,
                )
                zip.extractall(path="temp/")
    except IOError as err:
        logging.error(err)
        return -1


def untar(file, force):
    if not tarfile.is_tarfile(file):
        logging.error("Error: Not a tar file")
        return -1
    logging.info("Extracting: " + file)
    try:
        with tarfile.open(file, "r") as tar:
            for f in tar.getmembers():
                try:
                    tar.extract(f, set_attrs=False, path="temp/")
                except IOError:
                    continue
                except Exception as err:
                    logging.error(err)
                    return -1
    except IOError as err:
        logging.error(err)
        return -1


def compile(nodes, sample, root, force):
    content_files = []
    for node in nodes:
        create_dir(root + "/" + node, force=force)

    print()
    for node in nodes:
        print(node)
        # if (logging.DEBUG == level) or (logging.INFO == level):
        print("RUNNING:EXTRACT FILES")
        path = ["", ""]
        try:
            path[0] = str(extract_file(node, sample, "zip", force))
            path[1] = str(extract_file(node, sample, "tar.gz", force))
        except RuntimeError as err:
            err.add_note("Data files must be exist!")
            raise err

        content_files += [node]

        for i in range(0, len(path)):
            path[i] = os.path.normpath("temp/" + str(path[i]))

        print("RUNNING:GET DETAILS")
        try:
            content = get_detail(node, path)
        except RuntimeError:
            raise

        # DRAW IMAGES FOR CONTENT
        print("RUNNING:DRAW IMAGES")
        try:
            images = drw_content(path, os.path.normpath(root + "/" +
                                                        node + "/"))
        except RuntimeError as err:
            raise err
        # END DRAWING
        print("RUNNING:SAVE IMAGES")
        try:
            # SAVE IMAGE NAME
            tools.save_json(
                os.path.normpath(root + "/" + node + "/images.json"), images
            )
            # SAVE INFORMATION
            tools.save_json(
                os.path.normpath(root + "/" + node + "/" +
                                 node + ".json"), content
                )
        except RuntimeError as err:
            raise err

        print("DONE")
        print()

    sys.stdout.write("\033[?25h")
    return content_files


def create_dir(path, force=False):
    try:
        os.mkdir(os.path.normpath(path))
        logging.info("Folder created: " + path)
    except FileExistsError:
        if not os.listdir(path):
            return
        if force:
            clean_up(
                path=os.path.normpath(path),
                prompt="Do you want to replace it?",
                force=force,
            )
        else:
            print(path + " folder exist!")
            clean_up(
                path=os.path.normpath(path),
                prompt="Do you want to replace it?",
                force=force,
            )


# Flow of program
def run(nodes, sample, output, force):
    out_dir = os.path.split(output)[0]

    # Create output and temp directory
    create_dir(os.path.normpath(out_dir), force)
    try:
        os.mkdir(os.path.normpath("temp"))
    except FileExistsError:
        pass

    # Fetch and cook images from logs
    try:
        content_files = compile(nodes, sample, out_dir, force)
    except RuntimeError:
        print("Aborted")
        raise

    if content_files == -1:
        print("Error: ", end='')
        print("No files to join!")
        return -1

    # Union all jsons to one file
    tools.join_json(content_files, output)


# END_IMPLEMENTATION


# ****************************************
# MAIN
# ****************************************
def main():
    print("------------------------------")
    print("RUNNING AS A STANDALONE MODULE")
    print("------------------------------")
    data_object = {
            "nodes_name": ["DBMC01", "DBMC02", "DBMC-DR"],
            "logs_dir": './sample/',
            "output_file": "output/solaris.json",
            "force_mode": False,
            "type": "Standalone",
            "platform": "Linux"
            }
    run(nodes=data_object["nodes_name"],
        sample=data_object["logs_dir"],
        output=data_object["output_file"],
        force=data_object["force_mode"])
    pass


if __name__ == "__main__":
    main()
# ****************************************
# END MAIN
# ****************************************
