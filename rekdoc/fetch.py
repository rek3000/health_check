# -------------------
# SYSTEM DATA FETCHER
# -------------------

__version__ = "1.0"
__author__ = "Rek"

# Standard Library
import os
import io
import sys
import datetime
import shutil
import glob
import json
import zipfile
import tarfile
import logging

# Local library
from rekdoc import tools
from rekdoc import const


# ------------------------------
# DECORATORS
# ------------------------------
def debug(func):
    def _debug(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__}(args: {args}, kwargs: {kwargs}) -> {result}")
        return result

    return _debug
# ------------------------------
# END DECORATORS
# ------------------------------


# ------------------------------
# HELPER
# ------------------------------
def extract_file(file, compress, force):
    compress = compress.lower()
    if compress == "zip":
        unzip(file, force)
        dir = tools.rm_ext(file, compress)
        path = os.path.split(dir)[1]
        return path
    elif compress == "tar.gz":
        untar(file, compress, force)
        dir = tools.rm_ext(file, compress)
        path = os.path.split(dir)[1]
        return path
    elif compress == "gz":
        untar(file, compress, force)
        dir = tools.rm_ext(file, compress)
        path = os.path.split(dir)[1]
        return path
    # else:
    #     raise RuntimeError("Cannot extract file")


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


def untar(file_path, compress, force):
    if not tarfile.is_tarfile(file_path):
        logging.error("Error: Not a tar file")
        return -1
    logging.info("Extracting: " + file_path)
    filename = os.path.split(file_path)[-1]
    if compress == "gz":
        extract_folder = os.path.join(
            "./temp", tools.rm_ext(filename, compress))
    else:
        extract_folder = "temp/"
    try:
        with tarfile.open(file_path, "r") as tar:
            for f in tar.getmembers():
                try:
                    tar.extract(f, set_attrs=False, path=extract_folder)
                except IOError:
                    continue
                except Exception as err:
                    logging.error(err)
                    return -1

        if compress == "gz":
            archive_folder = os.path.join(extract_folder, 'archive')
            if os.path.exists(archive_folder) and os.path.isdir(archive_folder):
                for item in os.listdir(archive_folder):
                    item_path = os.path.join(archive_folder, item)
                    if os.path.isfile(item_path):
                        shutil.move(item_path, extract_folder)
                    elif os.path.isdir(item_path):
                        shutil.move(item_path,
                                    os.path.join(extract_folder, item))
                os.rmdir(archive_folder)

    except IOError as err:
        logging.error(err)
        raise


# Find the file matched with keyword(regular expression)
def get_file(regex, logs_dir):
    path = logs_dir + regex
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
        print(prompt + "[y/n]", end="")
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
# ------------------------------
# END HELPER
# ------------------------------


# ------------------------------
# IMAGE PROCESSING
# ------------------------------
# DRAW ILOM
def drw_fault(path, out_dir):
    fault = io.StringIO()
    fault.write(path + const.FAULT + "\n")
    stdout = tools.cat(os.path.normpath(path + const.FAULT))
    fault.write(str(stdout))
    tools.drw_text_image(fault, os.path.normpath(out_dir + "/fault.png"))


def drw_temp(path, out_dir):
    temp = io.StringIO()
    temp.write(path + const.TEMP + "\n")
    reg = "^ /System/Cooling$"
    stdout = tools.grep(os.path.normpath(path + const.TEMP), reg, False, 9)
    for line in stdout:
        temp.write(str(line) + "\n")
    tools.drw_text_image(temp, os.path.normpath(out_dir + "/temp.png"))


def drw_firmware(path, out_dir):
    firmware = io.StringIO()
    firmware.write(path + const.FIRMWARE + "\n")
    reg = "^Oracle"
    stdout = tools.grep(os.path.normpath(path + const.FIRMWARE), reg, True, 5)
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
    image.write(path + const.IMAGE_SOL + "\n")
    image.write(tools.cat(os.path.normpath(path + const.IMAGE_SOL)))
    tools.drw_text_image(image, os.path.normpath(out_dir + "/image.png"))
    return image


def drw_vol(path, out_dir):
    vol = io.StringIO()
    vol.write(path + const.PARTITION_SOL + "\n")
    vol.write(tools.cat(os.path.normpath(path + const.PARTITION_SOL)))
    tools.drw_text_image(vol, os.path.normpath(out_dir + "/vol.png"))
    return vol


def drw_raid(path, out_dir):
    raid = io.StringIO()
    raid.write(path + const.RAID_SOL + "\n")
    raid.write(tools.cat(os.path.normpath(path + const.RAID_SOL)))
    tools.drw_text_image(raid, os.path.normpath(out_dir + "/raid.png"))
    return raid


def drw_net(path, out_dir):
    net = io.StringIO()
    net.write(path + const.NETWORK_SOL + "\n")
    net.write(tools.cat(os.path.normpath(path + const.NETWORK_SOL)))
    tools.drw_text_image(net, os.path.normpath(out_dir + "/net.png"))
    return net


def drw_cpu(path, out_dir):
    cpu_idle = io.StringIO()
    cpu_idle.write(path + const.CPU_ULTILIZATION_SOL + "\n")
    cpu_idle.write(tools.cat(os.path.normpath(path +
                                              const.CPU_ULTILIZATION_SOL)))
    tools.drw_text_image(cpu_idle, os.path.normpath(out_dir + "/cpu_idle.png"))
    return cpu_idle


def drw_load(path, out_dir):
    load = io.StringIO()
    load.write(path + const.CPU_LOAD_SOL + "\n")
    load.write(tools.cat(os.path.normpath(path + const.CPU_LOAD_SOL)))
    tools.drw_text_image(load, os.path.normpath(out_dir + "/load.png"))
    return load


def drw_mem(path, out_dir):
    mem = io.StringIO()
    mem.write(path + const.MEM_SOL + "\n")
    mem.write(tools.cat(os.path.normpath(path + const.MEM_SOL)))
    tools.drw_text_image(mem, os.path.normpath(out_dir + "/mem.png"))
    return mem


def drw_swap(path, out_dir):
    swap = io.StringIO()
    swap.write(path + const.SWAP_SOL + "\n")
    swap.write(tools.cat(os.path.normpath(path + const.SWAP_SOL)))
    tools.drw_text_image(swap, os.path.normpath(out_dir + "/swap.png"))
    return swap


# SUCKS, rewrite later
def drw_system_status(path, out_dir):
    drw_image(path, out_dir)
    drw_vol(path, out_dir)
    drw_raid(path, out_dir)
    drw_net(path, out_dir)
    return [
            "image.png",
            ["vol.png", "raid.png"],
            "net.png",
            ]


def drw_system_performance(path, out_dir):
    drw_cpu(path, out_dir)
    drw_load(path, out_dir)
    drw_mem(path, out_dir)
    drw_swap(path, out_dir)
    return [
            "cpu_idle.png",
            "load.png",
            "mem.png",
            "swap.png",
            ]


def drw_content(path, out_dir):
    ilom = drw_ilom(path[0], out_dir)
    system_status = drw_system_status(path[1], out_dir)
    system_performance = drw_system_performance(path[2], out_dir)
    images = ilom + system_status + system_performance
    logging.info(images)
    return images


# ------------------------------
# FETCH ILOM
# ------------------------------
def get_fault(path):
    try:
        stdout = tools.grep(os.path.normpath(path + const.FAULT), "*", True, 9)
        fault = stdout.strip()
        return fault
    except RuntimeError:
        print("Failed to fetch fault data")
        raise


def get_temp(path):
    try:
        temps = tools.grep(
            os.path.normpath(path + const.TEMP), "^ /System/Cooling$", False, 9
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
        stdout = tools.grep(os.path.normpath(path + const.FIRMWARE),
                            "Version", True)
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
# ------------------------------
# END FETCH ILOM
# ------------------------------


# ------------------------------
# FETCH OS
# ------------------------------
def get_image(path):
    try:
        stdout = tools.grep(os.path.normpath(path + const.IMAGE_SOL),
                            "Solaris", True)
        image = stdout.strip().split()
        image = image[2]
        return image
    except RuntimeError:
        print("Failed to fetch image")
        raise


def get_vol(path):
    try:
        stdout = tools.grep(os.path.normpath(path + const.PARTITION_SOL),
                            "\\B/$", True)
        vol = stdout.strip().split()
        vol = vol[-2]
        return vol
    except RuntimeError:
        print("Failed to fetch volume")
        raise


def get_raid(path):
    try:
        stdout = tools.grep(os.path.normpath(path + const.RAID_SOL),
                            "mirror", True)
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
        net_ipmp = tools.grep(os.path.normpath(path + const.NETWORK_SOL),
                              "ipmp", True)
        net_aggr = tools.grep(os.path.normpath(path + const.NETWORK_SOL),
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
        cpu_util_path = os.path.normpath(
            path + const.CPU_ULTILIZATION_SOL + '*.dat')
        files = glob.glob(cpu_util_path, recursive=True)
        cpu_idle_alltime = []
        for file in files:
            stdout_lines = tools.grep(
                file, "CPU states:", False)
            cpu_idle_perfile_list = [float(stdout.split()[2][:-1])
                                     for stdout in stdout_lines]
            cpu_idle_perfile = sum(cpu_idle_perfile_list) / \
                len(cpu_idle_perfile_list)
            cpu_idle_alltime.append(cpu_idle_perfile)
            logging.debug("CPU IDLE")
            logging.debug(cpu_idle_perfile_list)
        cpu_idle = float("{:.2f}".format(
            sum(cpu_idle_alltime) / len(cpu_idle_alltime)))
        cpu_util = float("{:.2f}".format(100 - cpu_idle))
        logging.info("CPU_IDLE:" + str(cpu_idle))
        logging.info("CPU_UTIL:" + str(cpu_util))
        return [cpu_util, cpu_idle]
    except RuntimeError:
        print("Failed to feth cpu util")
        raise


def get_load_avg(path):
    try:
        stdout = tools.grep(os.path.normpath(path + const.CPU_LOAD_SOL),
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
        stdout = tools.grep(
            os.path.normpath(path + const.VCPU_SOL),
            "Status", single_match=False
        )
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


def get_mem_free(path):
    try:
        mem_free_path = os.path.normpath(path + const.MEM_SOL + '*.dat')
        files = glob.glob(mem_free_path, recursive=True)
        mem_free_alltime = []
        total_mem = float(tools.grep(
            files[-1], "Memory", True).split()[1][:-1])
        for file in files:
            stdout_lines = tools.grep(
                file, "Memory", False)
            mem_free_perfile_list = [float(stdout.split()[4][:-1])
                                     for stdout in stdout_lines]
            mem_free_perfile = sum(mem_free_perfile_list) / \
                len(mem_free_perfile_list)
            mem_free_alltime.append(mem_free_perfile)
            logging.debug("MEM FREE")
            logging.debug(mem_free_perfile_list)
        mem_free = float("{:.0f}".format(
            sum(mem_free_alltime) / len(mem_free_alltime)))
        # mem_util = float("{:.0f}".format(total_mem - mem_free))
        mem_free_percent = float("{:.2f}".format((mem_free / total_mem) * 100))
        mem_util_percent = 100 - mem_free_percent
        logging.info("MEM_FREE:" + str(mem_free_percent))
        logging.info("MEM_UTIL:" + str(mem_util_percent))
        return mem_free_percent, mem_util_percent
    except RuntimeError:
        print("Failed to fetch memory util")
        raise


def get_io_busy(path):
    try:
        io_busy_path = os.path.normpath(path + const.IO_SOL + '*.dat')
        files = glob.glob(io_busy_path, recursive=True)
        io_busy_alltime = []
        for file in files:
            # check_times = len(tools.grep(file, "zzz", False))
            stdout = tools.cat(file, True)
            io_busy_perfile_list = []
            io_busy_persection_list = []
            io_busy_persection = []
            for i in range(1, len(stdout)):
                if "zzz" in stdout[i]:
                    if i == len(stdout) - 1:
                        break
                    i = i + 2
                    logging.debug(json.dumps(
                        io_busy_persection_list, indent=2))
                    io_busy_persection = sum(
                        io_busy_persection_list) / len(io_busy_persection_list)
                    io_busy_perfile_list.append(io_busy_persection)
                    io_busy_persection_list = []
                    io_busy_persection = []
                    continue
                io_busy_persection_list.append(float(stdout[i].split()[-2]))
            io_busy_perfile = sum(io_busy_perfile_list) / \
                len(io_busy_perfile_list)
            io_busy_alltime.append(io_busy_perfile)
        io_busy = float("{:.0f}".format(
            sum(io_busy_alltime) / len(io_busy_alltime)))
        return io_busy

    except RuntimeError:
        print("Failed to fetch io busy")
        raise


def get_swap_util(path):
    try:
        stdout = tools.cat(os.path.normpath(path + const.SWAP_SOL))
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


def get_system_status(path, platform, server_type):
    x = {}
    try:
        if platform == "solaris":
            image = get_image(path)

            vol = get_vol(path)
            vol_avail = 100 - int(vol[:-1])
            x["image"] = image
            x["vol_avail"] = vol_avail

            raid_stat = get_raid(path)
            x["raid_stat"] = raid_stat

            bonding = get_bonding(path)
            x["bonding"] = bonding
        elif platform == "linux":
            pass
        elif platform == "exa":
            pass
        else:
            print("Failed to fetch OS information")
            raise RuntimeError()
    except RuntimeError:
        print("Failed to fetch OS information")
        raise
    return x


def get_system_perform(path, system_type, platform):
    x = {}
    try:
        if system_type == "standalone":
            if platform == "solaris":
                cpu_util = get_cpu_util(path)[0]
                x["cpu_util"] = cpu_util

                # load = get_load(path)
                # x["load"] = {}
                # x["load"]["load_avg"] = load[0]
                # x["load"]["vcpu"] = load[1]
                # x["load"]["load_avg_per"] = load[2]
                mem_free = get_mem_free(path)[0]
                x["mem_free"] = mem_free

                # io_busy = get_io_busy(path)[0]
                # x["io_busy"] = io_busy

                # swap_util = get_swap_util(path)[1]
                # x["swap_util"] = swap_util
            elif platform == "linux":
                pass
        elif system_type == "exa":
            pass
    except RuntimeError:
        print("Failed to fetch OS information")
        raise
    return x
# ------------------------------
# END FETCH OS
# ------------------------------


def get_detail(node, path):
    ilom = {}
    system_status = {}
    system_perform = {}
    try:
        ilom = get_ilom(path[0])
        # OSWatcher
        if system_info["system_type"] == "standalone":
            system_status = get_system_status(path[1],
                                              system_info["platform"],
                                              system_info["type"])
            system_perform = get_system_perform(path[2],
                                                system_info["system_type"],
                                                system_info["platform"])
        # ExaWatcher
        elif system_info["system_type"] == "exa":
            system_status = get_system_status(path[1],
                                              system_info["system_type"],
                                              system_info["type"])

            system_perform = get_system_perform(path[1],
                                                system_info["system_type"],
                                                system_info["platform"])
        else:
            raise RuntimeError
    except RuntimeError:
        raise
    name = node

    content = {}
    # logging.info(json.dumps(ilom, indent=2))
    # logging.info(json.dumps(system_status, indent=2))
    # logging.info(json.dumps(system_perform, indent=2))
    content[name] = {**ilom,
                     **system_status,
                     **system_perform}
    logging.info("JSON file: " +
                 json.dumps(content, indent=2, ensure_ascii=False))
    return content


##### FETCH OVERVIEW #####
def get_product(path):
    product = tools.grep(os.path.normpath(path + const.PRODUCT),
                         "product_name", True)
    return product


def get_serial(path):
    serial = tools.grep(os.path.normpath(path + const.SERIAL),
                        "serial_number", True)
    return serial


def get_ip(path):
    # ip = grep(os.path.normpath(path + NETWORK_SOL), "serial_number", True)
    pass


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
##### END OVERVIEW #####


def compile(nodes_name, logs_dir, out_dir, force):
    content_files = []
    list_file_logs = []
    print("CHOOSE FILE TO EXTRACT")
    for node in nodes_name:
        create_dir(out_dir + "/" + node, force=force)
        try:
            file_logs = ["", "", ""]
            print("NODE:" + node)
            print("-----------------------------")

            print("ILOM SNAPSHOT")
            file_logs[0] = get_file("*.zip", logs_dir)
            print("EXPLORER")
            file_logs[1] = get_file("*.tar.gz", logs_dir)
            print("OSWATCHER")
            file_logs[2] = get_file("archive*.gz", logs_dir)
            list_file_logs.append(file_logs)
            print()
        except RuntimeError as err:
            err.add_note("Data files must be exist!")
            raise err

    print("-----------------------------")
    for node in nodes_name:
        print(node)
        list_logs_dir = ["", "", ""]
        file_logs = []
        print("RUNNING:EXTRACT FILES")
        file_logs = list_file_logs[nodes_name.index(node)]
        print("RUNNING:EXTRACT ILOM SNAPSHOT")
        list_logs_dir[0] = extract_file(file_logs[0], "zip", force)
        print("RUNNING:EXTRACT EXPLORER")
        list_logs_dir[1] = extract_file(file_logs[1], "tar.gz", force)
        print("RUNNING:EXTRACT OSWATCHER")
        list_logs_dir[2] = extract_file(file_logs[2], "gz", force)

        content_files.append(os.path.normpath(out_dir + "/" +
                                              node + "/" + node + ".json"))

        list_logs_dir = [os.path.normpath(
            "temp/" + logs_dir) for logs_dir in list_logs_dir]
        logging.info(json.dumps(list_logs_dir, indent=2))

        print("RUNNING:GET DETAILS")
        try:
            content = get_detail(node, list_logs_dir)
        except RuntimeError:
            raise

        # DRAW IMAGES FOR CONTENT
        print("RUNNING:DRAW IMAGES")
        try:
            images = drw_content(list_logs_dir,
                                 os.path.normpath(out_dir + "/" + node + "/"))
        except RuntimeError as err:
            raise err
        # END DRAWING
        print("RUNNING:SAVE IMAGES")
        try:
            # SAVE IMAGE NAME
            tools.save_json(
                os.path.normpath(out_dir + "/" + node + "/images.json"), images
            )
            # SAVE INFORMATION
            tools.save_json(
                os.path.normpath(out_dir + "/" + node +
                                 "/" + node + ".json"), content
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


TYPES = ["baremetal", "vm"]
SYSTEM = ["standalone", "exa"]
PLATFORM = ["linux", "solaris"]

system_info = {
    "system_type": "",
    "platform": "",
    "type": "",
}


def set_system_info():
    while True:
        try:
            c = str(input("System Type [standalone|exa]?\n [standalone] ")
                    or "standalone")
            if (c != "standalone") and (c != "exa"):
                continue
            system_info["system_type"] = c
        except KeyboardInterrupt:
            print()
            sys.exit()
        break

    while True:
        try:
            c = str(input("Platform [linux|solaris]?\n [solaris] ")
                    or "solaris")
            if (c != "linux") and (c != "solaris"):
                continue
            system_info["platform"] = c
        except KeyboardInterrupt:
            print()
            sys.exit()
        break

    while True:
        try:
            c = str(input("Type [baremetal|vm]?\n [baremetal] ")
                    or "baremetal")
            if (c != "baremetal") and (c != "vm"):
                continue
            system_info["type"] = c
        except KeyboardInterrupt:
            print()
            sys.exit()
        break
    print(json.dumps(system_info, indent=2))


# Flow of program
def run(nodes_name, logs_dir, out_dir, force):
    set_system_info()
    # Create output and temp directory
    try:
        os.mkdir(os.path.normpath("temp"))
        os.mkdir(os.path.normpath(out_dir))
    except FileExistsError:
        pass
    # create_dir(os.path.normpath(out_dir), force)
    root_dir = out_dir + "/" + str(datetime.datetime.now())
    create_dir(os.path.normpath(root_dir))
    # create root folder

    # Fetch and cook images from logs
    try:
        content_files = compile(nodes_name, logs_dir, root_dir, force)
        logging.info(content_files)
    except RuntimeError:
        print("Aborted")
        raise

    if content_files == -1:
        print("Error: ", end="")
        print("No files to join!")
        return -1

    # Union all jsons to one file
    out_file = os.path.normpath(root_dir + "/" + "summary.json")
    tools.join_json(content_files, out_file)
    return out_file


# END_IMPLEMENTATION


# ------------------------------
# MAIN
# ------------------------------


def main():
    print("------------------------------")
    print("RUNNING AS A STANDALONE MODULE")
    print("------------------------------")

    data_object = {
        "nodes_name": ["DBMC01", "DBMC02", "DBMC-DR"],
        "logs_dir": "./sample/",
        "output_file": "output/solaris.json",
        "force": False,
    }

    run(
        nodes_name=data_object["nodes_name"],
        logs_dir=data_object["logs_dir"],
        output_file=data_object["output_file"],
        force=data_object["force"],
    )
    pass


if __name__ == "__main__":
    main()
# ****************************************
# END MAIN
# ****************************************
