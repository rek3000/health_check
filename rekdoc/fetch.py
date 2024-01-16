# -------------------
# SYSTEM DATA FETCHER
# -------------------
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

TYPES = ["baremetal", "vm"]
SYSTEM = ["standalone", "exa"]
PLATFORM = ["linux", "solaris"]

system_info = {
    "system_type": "",
    "platform": "",
    "type": "",
}


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
    if file == "":
        return ""
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
            if os.path.exists(archive_folder) \
                    and os.path.isdir(archive_folder):
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
        print("[-1]. Skip")
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
        if c == -1:
            return ""
        else:
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


def clean_up(path, prompt="Remove files?", force=False):
    if force:
        clean_files(path)
    else:
        print(prompt + "[y/n]", end="")
        choice = input() or "\n"

        if choice in ["\n", "y", "yes"]:
            clean_files(path)


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
    if system_info["type"] == "baremetal":
        fault.write(path + const.FAULT + "\n")
        stdout = tools.cat(os.path.normpath(path + const.FAULT))
        fault.write(str(stdout))
        tools.drw_text_image(fault, os.path.normpath(out_dir + "/fault.png"))
    else:
        fault.write(path + const.FAULT_SOL + "\n")
        stdout = tools.cat(os.path.normpath(path + const.FAULT_SOL))
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
    if system_info["type"] == "baremetal":
        drw_fault(path, out_dir)
        drw_temp(path, out_dir)
        drw_firmware(path, out_dir)
        return ["ilom/fault.png", "ilom/temp.png", "ilom/firmware.png"]


## END DRAW ILOM ##


## DRAW OF ##
def drw_image(path, out_dir):
    image = io.StringIO()
    image.write(path + const.IMAGE_SOL + "\n")
    image.write(tools.grep(os.path.normpath(
        path + const.IMAGE_SOL), "Name: entire", True, 18))
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
    if system_info["type"] == "baremetal":
        drw_image(path, out_dir)
        drw_vol(path, out_dir)
        drw_raid(path, out_dir)
        drw_net(path, out_dir)
        return [
            "status/image.png",
            ["status/vol.png", "status/raid.png"],
            "status/net.png",
        ]
    else:
        drw_image(path, out_dir)
        drw_vol(path, out_dir)
        return [
            "status/image.png",
            ["status/vol.png", ""],
        ]


def drw_system_performance(path, out_dir):
    # drw_cpu(path, out_dir)
    # drw_load(path, out_dir)
    # drw_mem(path, out_dir)
    # drw_swap(path, out_dir)
    try:
        log_name = os.path.split(path)[1]
        command = ["java", "-jar", "oswbba.jar",
                   "-i", path,
                   "-D", log_name
                   ]
        tools.run(command, False)

        dashboard_dir = os.path.normpath(
            "analysis/" + log_name + "/dashboard/generated_files/")
        shutil.copy(os.path.normpath(dashboard_dir +
                    "/OSWg_OS_Cpu_Util.jpg"), out_dir)
        shutil.copy(os.path.normpath(dashboard_dir +
                    "/OSWg_OS_Memory_Free.jpg"), out_dir)
        shutil.copy(os.path.normpath(
            dashboard_dir + "/OSWg_OS_IO_PB.jpg"), out_dir)
    except Exception as err:
        print(err)
    return ["perform/OSWg_OS_Cpu_Util.jpg",
            "perform/OSWg_OS_Memory_Free.jpg",
            "perform/OSWg_OS_IO_PB.jpg"]
    # return [
    #     "cpu_idle.png",
    #     "load.png",
    #     "mem.png",
    #     "swap.png",
    # ]


def drw_content(path, out_dir):
    ilom = []
    if system_info["type"] == "baremetal":
        ilom = drw_ilom(path[0], out_dir + "/ilom")
    else:
        drw_fault(path[1], out_dir + "/ilom")
        ilom = ["fault.png"]
    system_status = drw_system_status(path[1], out_dir + "/status")
    system_performance = drw_system_performance(path[2], out_dir + "/perform")
    # system_performance = ["OSWg_OS_Cpu_Idle.jpg",
    #                       "OSWg_OS_Memory_Free.jpg",
    #                       "OSWg_OS_IO_PB.jpg"]
    images = ilom + system_status + system_performance
    logging.info(images)
    return images


# ------------------------------
# FETCH ILOM
# ------------------------------
def get_fault(path):
    fault = ""
    if system_info["type"] == "vm":
        try:
            if tools.grep(os.path.normpath(path + const.FAULT_SOL), "critical", True):
                fault = "critical"
            elif tools.grep(os.path.normpath(path + const.FAULT_SOL), "warning", True):
                fault = "warning"
            else:
                stdout = tools.grep(os.path.normpath(
                    path + const.FAULT), ".", True, 9)
                fault = stdout.strip()
            return fault
        except RuntimeError:
            return fault
        except Exception:
            print("Failed to fetch fault data")
            raise
    try:
        if tools.grep(os.path.normpath(path + const.FAULT), "critical", True):
            fault = "critical"
        elif tools.grep(os.path.normpath(path + const.FAULT), "warning", True):
            fault = "warning"
        else:
            stdout = tools.grep(os.path.normpath(
                path + const.FAULT), ".", True, 9)
            fault = stdout.strip()
        return fault
    except RuntimeError:
        return fault
    except Exception:
        print("Failed to fetch fault data")
        raise


def get_temp(path):
    inlet_temp = ""
    exhaust_temp = ""
    try:
        temps = tools.grep(
            os.path.normpath(path + const.TEMP), "^ /System/Cooling$", False, 9
        )
        for line in temps:
            if "inlet_temp" in line:
                inlet_temp = " ".join(line.split()[2:5])
                continue
            elif "exhaust_temp" in line:
                exhaust_temp = " ".join(line.split()[2:5])
                continue
        return inlet_temp, exhaust_temp
    except RuntimeError:
        return inlet_temp, exhaust_temp
    except Exception:
        print("Failed to fetch temperature")
        raise


def get_firmware(path):
    firmware = ""
    try:
        stdout = tools.grep(os.path.normpath(path + const.FIRMWARE),
                            "Version", True)
        firmware = " ".join(stdout.strip("\r\n").split()[1:])
        return firmware
    except RuntimeError:
        return firmware
    except Exception:
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
    image = ""
    try:
        stdout = tools.grep(os.path.normpath(path + const.IMAGE_SOL),
                            "Name: entire", True, 15)
        image_lines = stdout.split('\n')
        for line in image_lines:
            if "Version" in line:
                image = line.split()[4][:-1]
                break
        return image
    except RuntimeError:
        return image
    except Exception:
        print("Failed to fetch image")
        raise


def get_vol(path):
    vol = ""
    try:
        stdout = tools.grep(os.path.normpath(path + const.PARTITION_SOL),
                            "\\B/$", True)
        vol = stdout.strip().split()
        vol = vol[-2]
        return vol
    except RuntimeError:
        return vol
    except Exception:
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
    bonding = ""
    try:
        net_ipmp = tools.grep(os.path.normpath(path + const.NETWORK_SOL),
                              "ipmp", True)
        net_aggr = tools.grep(os.path.normpath(path + const.NETWORK_SOL_AGGR),
                              "up", True)
        if not net_ipmp and not net_aggr:
            bonding = "none"
        elif net_ipmp and not net_aggr:
            # bonding = "ipmp"
            state = net_ipmp.split()[2]
            if state == "ok":
                bonding = "ipmp"
        elif net_aggr and not net_ipmp:
            state = net_aggr.split()[4]
            if state == "up":
                bonding = "aggr"
        else:
            bonding = "both"
        return bonding
    except RuntimeError:
        return bonding
    except Exception:
        print("Failed to fetch bonding status")
        raise


def get_cpu_util(path):
    cpu_util = ""
    cpu_idle = ""
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
        return [cpu_util, cpu_idle]
    except Exception:
        print("Failed to feth cpu util")
        raise


def get_load_avg(path):
    load_avg = ""
    try:
        stdout = tools.grep(os.path.normpath(path + const.CPU_LOAD_SOL),
                            "load average", True)
        load = stdout.strip().split(", ")
        load_avg = " ".join(load).split()[-3:]
        load_avg = float(max(load_avg))
        return load_avg
    except RuntimeError:
        return load_avg
    except Exception:
        print("Failed to get load average")
        raise


def get_vcpu(path):
    vcpu = ""
    try:
        stdout = tools.grep(
            os.path.normpath(path + const.VCPU_SOL),
            "Status", single_match=False
        )
        vcpu = stdout[-1].split()[4]
        vcpu = int(vcpu) + 1
        return vcpu
    except RuntimeError:
        return vcpu
    except Exception:
        print("Failed to fetch VCPU")
        raise


def get_load(path):
    load_avg, vcpu, load_avg_per = ""
    try:
        load_avg = get_load_avg(path)
        vcpu = get_vcpu(path)
        load_avg_per = load_avg / vcpu
        load_avg_per = float(f"{load_avg_per:.3f}")
        return load_avg, vcpu, load_avg_per
    except RuntimeError:
        return load_avg, vcpu, load_avg_per
    except Exception:
        print("Failed to fetch load")
        raise


def get_mem_free(path):
    mem_free_percent = ""
    mem_util_percent = ""
    x = {"mem_free_percent": 0,
         "mem_free": 0,
         "total_mem": 0}
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
        if mem_free > total_mem:
            mem_free = mem_free / 1024
        # mem_util = float("{:.0f}".format(total_mem - mem_free))
        mem_free_percent = float("{:.2f}".format((mem_free / total_mem) * 100))
        mem_util_percent = 100 - mem_free_percent
        logging.info("MEM_FREE:" + str(mem_free_percent))
        logging.info("MEM_UTIL:" + str(mem_util_percent))
        x["mem_free_percent"] = mem_free_percent
        x["mem_free"] = mem_free
        x["total_mem"] = total_mem
        return x
    except RuntimeError:
        return x
        # return mem_free_percent, mem_util_percent
    except Exception:
        print("Failed to fetch memory util")
        raise


def get_io_busy(path):
    io_busy = ""
    try:
        io_busy_path = os.path.normpath(path + const.IO_SOL + '*.dat')
        files = glob.glob(io_busy_path, recursive=True)
        io_busy = {"name": None, "busy": 0}
        io_busy_list = []

        for file in files:
            stdout = tools.cat(file, True)
            io_busy_persection_list = []
            io_busy_perfile_list = []
            average_io_busy_persection = 0
            average_io_busy_perfile = 0
            i = 1
            # Evaluate each section in a file
            while i < len(stdout):
                if "zzz" in stdout[i]:
                    logging.debug("ZZZ")
                    logging.debug(json.dumps(
                        io_busy_persection_list, indent=2))
                    try:
                        try:
                            # maxbusy = max(io_busy_persection_list)
                            sorted_persection = sorted(
                                io_busy_persection_list, reverse=True)
                            average_io_busy_persection = sum(
                                sorted_persection[:4]) / 4
                            io_busy_perfile_list.append(
                                average_io_busy_persection)
                        except Exception:
                            i += 3
                            continue
                    except Exception as err:
                        print(err)
                    i += 3
                    continue
                io_busy_persection_list.append(float(stdout[i].split()[-2]))
                i += 1
            sorted_perfile = sorted(
                io_busy_perfile_list, reverse=True)
            average_io_busy_perfile = sum(sorted_perfile) / len(sorted_perfile)
            io_busy_list.append(average_io_busy_perfile)

        sorted_io_busy = sorted(io_busy_list, reverse=True)
        io_busy['busy'] = float("{:.2f}".format(
            sum(sorted_io_busy) / len(sorted_io_busy)))
        return io_busy
    except Exception as err:
        print(err)
        print("FAILED:fetch io busy")
        return io_busy


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

            if server_type == "baremetal":
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


def get_system_perform(path, platform, system_type):
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
                mem_free = get_mem_free(path)
                x["mem_free"] = mem_free

                # TODO
                io_busy = get_io_busy(path)
                x["io_busy"] = io_busy
                # filler
                # x["io_busy"] = ""

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


def get_detail(node, path, node_dir):
    ilom = {}
    system_status = {}
    system_perform = {}
    create_dir(node_dir + "/" + "ilom")
    create_dir(node_dir + "/" + "status")
    create_dir(node_dir + "/" + "perform")
    try:
        if path[0] == "" and system_info["type"] == "baremetal":
            ilom = {
                "fault": "",
                "inlet": "",
                "exhaust": "",
                "firmware": "",
            }
        elif system_info["type"] == "baremetal":
            ilom = get_ilom(path[0])
        else:
            ilom = {"fault": get_fault(path[1])}
        # OSWatcher
        if system_info["system_type"] == "standalone":
            if path[1] == "" and system_info["type"] == "baremetal":
                system_status = {
                    "image": "",
                    "vol_avail": "",
                    "raid_stat": "",
                    "bonding": ""
                }
            elif path[1] == "" and system_info["type"] == "vm":
                system_status = {
                    "image": "",
                    "vol_avail": "",
                }
            else:
                system_status = get_system_status(path[1],
                                                  system_info["platform"],
                                                  system_info["type"])
            if path[2] == "" and system_info["type"] == "baremetal":
                system_perform = {
                    "cpu_util": "",
                    "mem_free": "",
                    "io_busy": {"name": "",
                                "busy": ""}
                }
            else:
                system_perform = get_system_perform(path[2],
                                                    system_info["platform"],
                                                    system_info["system_type"])
        # ExaWatcher
        elif system_info["system_type"] == "exa":
            if path[1] == "":
                system_status = {
                    "image": "",
                    "vol_avail": "",
                    "raid_stat": "",
                    "bonding": ""
                }
            else:
                system_status = get_system_status(path[1],
                                                  system_info["system_type"],
                                                  system_info["type"])
            if path[2] == "":
                system_perform = {
                    "cpu_util": "",
                    "mem_free": "",
                }
            else:
                system_perform = get_system_perform(path[2],
                                                    system_info["platform"],
                                                    system_info["system_type"])
        else:
            raise RuntimeError
    except RuntimeError:
        raise
    name = node

    content = {"node_name": name,
               **ilom,
               **system_status,
               **system_perform}
    logging.info("JSON file: " +
                 json.dumps(content, indent=2, ensure_ascii=False))
    # Save information
    tools.save_json(os.path.normpath(
        node_dir + "/" + "ilom" + "/" + "ilom.json"), ilom)
    tools.save_json(os.path.normpath(node_dir + "/" + "status" +
                    "/" + "status.json"), system_status)
    tools.save_json(os.path.normpath(node_dir + "/" + "perform" +
                    "/" + "perform.json"), system_perform)
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


def compile(nodes_name, list_file_logs, out_dir, force):
    content_files = []
    print("CHOOSE FILE TO EXTRACT")

    print("-----------------------------")
    for node in nodes_name:
        node_dir = os.path.normpath(out_dir + "/" + node + "/")
        print(node)
        list_logs_dir = ["", "", ""]
        file_logs = []
        print("RUNNING:EXTRACT FILES")
        file_logs = list_file_logs[nodes_name.index(node)]
        print("RUNNING:EXTRACT ILOM SNAPSHOT")
        try:
            list_logs_dir[0] = extract_file(file_logs[0], "zip", force)
            print("RUNNING:EXTRACT EXPLORER")
            list_logs_dir[1] = extract_file(file_logs[1], "tar.gz", force)
            print("RUNNING:EXTRACT OSWATCHER")
            list_logs_dir[2] = extract_file(file_logs[2], "gz", force)
        except ValueError:
            pass

        content_files.append(os.path.normpath(node_dir + "/" + node + ".json"))

        list_logs_dir = [os.path.normpath(
            "temp/" + logs_dir) for logs_dir in list_logs_dir]
        for i in range(0, len(list_logs_dir)):
            if list_logs_dir[i] == "temp":
                list_logs_dir[i] = ""
        logging.info(json.dumps(list_logs_dir, indent=2))

        try:
            print("RUNNING:GET DETAILS")
            content = get_detail(node, list_logs_dir, node_dir)
            print("RUNNING:DRAW IMAGES")
            images = drw_content(list_logs_dir, node_dir)
            print("RUNNING:SAVE IMAGES")
            # Save image names
            tools.save_json(
                os.path.normpath(node_dir + "/" + "images.json"), images
            )
            # Save information
            tools.save_json(
                os.path.normpath(node_dir + "/" + node + ".json"), content
            )
            print("DONE")
            print()
        except RuntimeError:
            raise
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
def run(logs_dir, out_dir, force):
    # Create output and temp directory
    try:
        os.mkdir(os.path.normpath("temp"))
    except FileExistsError:
        pass
    try:
        os.mkdir(os.path.normpath(out_dir))
    except FileExistsError:
        pass
    root_dir = out_dir + "/" + str(datetime.datetime.now().isoformat())
    create_dir(os.path.normpath(root_dir))
    # create root folder

    i = 0
    list_alltime_logs = []
    summary_list = []
    while True:
        set_system_info()
        nodes_name = input(
            "Enter nodes' name (each separated by a space): ").split(" ")

        list_file_logs = []
        for node in nodes_name:
            create_dir(root_dir + "/" + node, force=force)
            try:
                file_logs = ["", "", ""]
                print("NODE:" + node)
                print("-----------------------------")

                print("ILOM SNAPSHOT")
                file_logs[0] = get_file("*.zip", logs_dir)
                print("EXPLORER")
                file_logs[1] = get_file("explorer*.tar.gz", logs_dir)
                print("OSWATCHER")
                file_logs[2] = get_file("archive*.gz", logs_dir)
                list_file_logs.append(file_logs)
                print()
            except RuntimeError as err:
                err.add_note("Data files must be exist!")
                raise err
        out_file = os.path.normpath(
            root_dir + "/" + "summary-" + str(i) + ".json")
        tools.save_json(out_file, system_info)
        summary_list.append(out_file)
        list_alltime_logs.append(list_file_logs)
        c = input("Run another time?[Y/N] ")
        if c in ["", "Y", "y", "yes", "Yes", "YES"]:
            i += 1
            continue
        else:
            break

    logging.debug(list_alltime_logs)
    for time in range(0, i):
        try:
            content_files = compile(
                nodes_name, list_alltime_logs[time], root_dir, force)
            logging.info(content_files)
        except RuntimeError:
            print("Aborted")
            raise
        tools.join_json(summary_list[time], content_files)

    if content_files == -1:
        print("Error: ", end="")
        print("No files to join!")
        return -1

    # Union all jsons to one file
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


if __name__ == "__main__":
    main()
# ****************************************
# END MAIN
# ****************************************
