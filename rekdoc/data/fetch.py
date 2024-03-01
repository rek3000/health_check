"""
    SYSTEM DATA FETCHER
Get system data from Logs
"""
# Standard Library
import os
import io
import sys
import datetime
import shutil
import json
import zipfile
import tarfile
from pathlib import Path
from rekdoc import core

# Local library
from rekdoc import tools
from rekdoc import const


# ------------------------------
# DECORATORS
# ------------------------------
def debug(func):
    def _debug(*args, **kwargs):
        result = func(*args, **kwargs)
        core.logger.debug(
            f"{func.__name__}(args: {args}, kwargs: {kwargs}) -> {result}")
        return result

    return _debug


# @debug
def extract_file(
        file: Path, compress: str,
        force: bool, exclude: list | None = None
) -> Path:
    """
    Extract Files with filter (exclude list).
Support "tar.gz", "gz" and "zip" files (ILOM, Explorer, OSWatcher)
    """
    compress = compress.lower()
    uncompressed = Path("")
    if not file:
        return ""

    if compress in ["tar.gz", "gz"]:
        untar(file, compress, force, exclude=exclude)
        uncompressed = Path(tools.rm_ext(str(file), compress)).name
    elif compress == "zip":
        unzip(file, force, exclude=exclude)
        uncompressed = Path(tools.rm_ext(str(file), compress)).name

    return uncompressed


def unzip(file: Path, force: bool, exclude: list | None = None):
    """
    Helper function to decompress zip file with filter.
    """
    if not zipfile.is_zipfile(file):
        core.logger.error(f"ERROR: {file} is NOT a ZIP file")
        return -1

    core.logger.info("EXTRACTING: " + file.name)

    try:
        with zipfile.ZipFile(file, "r") as zip_file:
            folder_name = "temp/"
            for member in zip_file.namelist():
                is_exist = any(os.path.normpath(folder_name + "/" + ex)
                               in member for ex in exclude)
                try:
                    if not is_exist:
                        zip_file.extract(member, path=folder_name)
                except (Exception, IOError) as err:
                    core.logger.error(err)
                    return -1

    except IOError as err:
        core.logger.error(err)
        return -1


def untar(file: Path, compress: str, force: bool, exclude: list | None = None):
    """
    Helper function to decompress tar file with filter.
    """
    if exclude is None:
        exclude = []

    if not tarfile.is_tarfile(file):
        core.logger.error(f"ERROR: {file} is Not a TAR file")
        return -1

    core.logger.info("EXTRACTING: " + file.name)
    filename = os.path.split(file)[-1]
    folder_name = tools.rm_ext(filename, compress)

    extract_folder = os.path.join(
        "temp/",
        folder_name) if compress == "gz" else "temp/"

    try:
        with tarfile.open(file, "r") as tar:
            for member in tar.getmembers():
                is_exist = any(os.path.normpath(folder_name + "/" + ex)
                               in member.name for ex in exclude)
                try:
                    if not is_exist:
                        tar.extract(member, set_attrs=False,
                                    path=extract_folder)
                except (Exception, IOError) as err:
                    core.logger.error(err)
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
        core.logger.error(err)
        raise

    return 0


# Find the file matched with keyword(regular expression)
def get_file(regex: str, logs_dir: Path) -> Path:
    """
    Choose a file from list of files
Print a list of files in the 'dir' and let user choose file through number.
    """
    # core.logger.debug(str(logs_dir))

    def print_files(files: list):
        for i, file in enumerate(files):
            print(f"[{i}] {file.name}")
        print("[-1] Skip")

    def get_user_input(files: list):
        while True:
            try:
                choice = int(input("Which file?\n [0] ") or "0")
                if choice == -1 or (0 <= choice < len(files)):
                    return choice
            except KeyboardInterrupt:
                print()
            except ValueError:
                continue

    files = sorted(logs_dir.glob(regex), reverse=True)

    try:
        print_files(files)
    except Exception:
        return ""
    choice = get_user_input(files)

    if choice == -1:
        return ""
    else:
        return files[choice]


def clean_files(dir):
    """
    Remove all files in "dir"
    """
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            core.logger.info("DELETED: " + file_path)
        except Exception as err:
            core.logger.error(f"FAILED to delete {file_path}. Reason: {err}")


def clean_up(path, prompt="Remove files?", force=False):
    if force or input(f"{prompt} [y/n] ").lower() in ["y", "yes"]:
        clean_files(path)


def clean_up_force(path):
    core.logger.error("FORCE CLEAN UP DUE TO ERROR!")
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
def drw_fault(path: Path, out_dir: Path, system_info: dict) -> None:
    fault = io.StringIO()
    if system_info["type"] == "baremetal":
        fault.write(str(path) + "/" + const.FAULT + "\n")
        stdout = tools.cat(path / const.FAULT)
        fault.write(str(stdout))
        tools.drw_text_image(fault, out_dir / "fault.png")
    else:
        fault.write(str(path) + const.FAULT_SOL + "\n")
        stdout = tools.cat(path / const.FAULT_SOL)
        fault.write(str(stdout))
        tools.drw_text_image(fault, out_dir / "fault.png")


def drw_temp(path: Path, out_dir: Path) -> None:
    temp = io.StringIO()
    temp.write(str(path) + "/" + const.TEMP + "\n")
    reg = "^ /System/Cooling$"
    stdout = tools.grep(path / const.TEMP, reg, False, 9)
    for line in stdout:
        temp.write(str(line) + "\n")
    tools.drw_text_image(temp, out_dir / "temp.png")


def drw_firmware(path: Path, out_dir: Path) -> None:
    firmware = io.StringIO()
    firmware.write(str(path) + "/" + const.FIRMWARE + "\n")
    reg = "^Oracle"
    stdout = tools.grep(path / const.FIRMWARE, reg, True, 5)
    firmware.write(str(stdout))
    tools.drw_text_image(firmware, out_dir / "firmware.png")


def drw_ilom(path: Path, out_dir: Path, system_info: dict) -> list:
    drw_fault(path, out_dir, system_info)
    drw_temp(path, out_dir)
    drw_firmware(path, out_dir)
    return ["ilom/fault.png", "ilom/temp.png", "ilom/firmware.png"]
# END DRAW ILOM


# DRAW
def drw_image(path: Path, out_dir: Path) -> str:
    image = io.StringIO()
    image.write(str(path) + "/" + const.IMAGE_SOL + "\n")
    stdout = tools.grep(path / const.IMAGE_SOL, "Name: entire", False, 18)
    for line in stdout:
        image.write(str(line) + "\n")
    tools.drw_text_image(image, out_dir / "image.png")
    return image


def drw_vol(path: Path, out_dir: Path) -> str:
    vol = io.StringIO()
    vol.write(str(path) + "/" + const.PARTITION_SOL + "\n")
    stdout = tools.cat(path / const.PARTITION_SOL, True)
    for line in stdout:
        vol.write(str(line) + "\n")
    tools.drw_text_image(vol, out_dir / "vol.png")
    return vol


def drw_raid(path: Path, out_dir: Path) -> str:
    raid = io.StringIO()
    raid.write(str(path) + "/" + const.RAID_SOL + "\n")
    stdout = tools.cat(path / const.RAID_SOL, True)
    for line in stdout:
        raid.write(str(line) + "\n")
    tools.drw_text_image(raid, out_dir / "raid.png")
    return raid


def drw_net(path: Path, out_dir: Path) -> str:
    net = io.StringIO()
    net.write(str(path) + "/" + const.NETWORK_SOL + "\n")
    stdout = tools.cat(path / const.NETWORK_SOL, True)
    for line in stdout:
        net.write(str(line) + "\n")
    tools.drw_text_image(net, out_dir / "net.png")
    return net


def drw_cpu(path: Path, out_dir: Path) -> str:
    cpu_idle = io.StringIO()
    cpu_idle.write(str(path) + "/" + const.CPU_ULTILIZATION_SOL + "\n")
    cpu_idle.write(tools.cat(path / const.CPU_ULTILIZATION_SOL))
    tools.drw_text_image(cpu_idle, out_dir / "cpu_idle.png")
    return cpu_idle


def drw_load(path: Path, out_dir: Path) -> str:
    load = io.StringIO()
    load.write(str(path) + "/" + const.CPU_LOAD_SOL + "\n")
    load.write(tools.cat(path / const.CPU_LOAD_SOL))
    tools.drw_text_image(load, out_dir / "load.png")
    return load


def drw_mem(path: Path, out_dir: Path) -> str:
    mem = io.StringIO()
    mem.write(str(path) + "/" + const.MEM_SOL + "\n")
    mem.write(tools.cat(path / const.MEM_SOL))
    tools.drw_text_image(mem, out_dir / "mem.png")
    return mem


def drw_swap(path: Path, out_dir: Path) -> str:
    swap = io.StringIO()
    swap.write(str(path) + "/" + const.SWAP_SOL + "\n")
    swap.write(tools.cat(path / const.SWAP_SOL))
    tools.drw_text_image(swap, out_dir / "swap.png")
    return swap


# rewrite later
def drw_system_status(path: Path, out_dir: Path, system_info: dict) -> list:
    """
    Draw System Status Images (Explorer) from Extracted Logs
    """
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


def drw_system_performance(
        path: Path, out_dir: Path, system_info: dict
) -> list:
    """
    Draw System Performance Images (OSWatcher) from Extracted Logs
Clarification: This just run the oswbba.jar file and
generate images from OSWatcher.
    """
    try:
        log_name = path.name
        command = ["java", "-jar", "/usr/share/java/oswbba.jar",
                   "-i", str(path),
                   "-D", log_name
                   ]
        tools.run(command, False)

        dashboard_dir = Path("analysis/") / log_name / \
            "dashboard/generated_files/"
        shutil.copy(dashboard_dir / "OSWg_OS_Cpu_Util.jpg", out_dir)
        shutil.copy(dashboard_dir / "OSWg_OS_Memory_Free.jpg", out_dir)
        shutil.copy(dashboard_dir / "OSWg_OS_IO_PB.jpg", out_dir)
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


def drw_content(path: Path, out_dir: Path, system_info: dict) -> list:
    ilom = []
    if system_info["type"] == "baremetal":
        ilom = drw_ilom(path[0], out_dir / "ilom", system_info)
    else:
        drw_fault(path[1], out_dir / "ilom", system_info)
        ilom = ["ilom/fault.png"]
    system_status = drw_system_status(
        path[1], out_dir / "status", system_info)
    system_performance = drw_system_performance(
        path[2], out_dir / "perform", system_info)
    images = ilom + system_status + system_performance
    core.logger.info(images)
    return images


# ------------------------------
# FETCH ILOM
# ------------------------------
def get_fault(path: Path, type: str) -> str:
    fault = ""

    if type == "vm":
        try:
            grep_result = tools.grep(
                path / const.FAULT_SOL, "(critical|warning)", True)
            if "critial" in grep_result:
                fault = "critical"
            elif "warning" in grep_result:
                fault = "warning"
            else:
                stdout = tools.grep(path / const.FAULT, ".", True, 9)
                fault = stdout.strip()

            return fault
        except (RuntimeError, Exception) as err:
            print(f"FAILED to fetch fault data: {err}")

    return fault


def get_temp(path: Path) -> (str, str):
    inlet_temp = ""
    exhaust_temp = ""

    try:
        temps = tools.grep(path / const.TEMP, "^ /System/Cooling$", False, 9)
        for line in temps:
            tokens = line.split()
            if "inlet_temp" in line:
                inlet_temp = " ".join(tokens[2:5])
            elif "exhaust_temp" in line:
                exhaust_temp = " ".join(tokens[2:5])

        return inlet_temp, exhaust_temp
    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch temperature: {err}")

    return inlet_temp, exhaust_temp


def get_firmware(path: Path) -> str:
    firmware = ""
    try:
        stdout = tools.grep(path / const.FIRMWARE, "Version", True)
        firmware_tokens = stdout.strip("\r\n").split()
        firmware = " ".join(firmware_tokens[1:])
        return firmware
    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch firmware: {err}")
    return firmware


def get_ilom(path: Path, system_info: dict) -> dict:
    try:
        fault = get_fault(path, system_info["type"])
        inlet_temp, exhaust_temp = get_temp(path)
        firmware = get_firmware(path)
    except RuntimeError:
        core.logger.error("Fetching ILOM is interrupted because of error")
        raise

    ilom = {
        "fault": fault,
        "inlet": inlet_temp,
        "exhaust": exhaust_temp,
        "firmware": firmware,
    }

    core.logger.debug(json.dumps(ilom, indent=2, ensure_ascii=False))

    return ilom
# ------------------------------
# END FETCH ILOM
# ------------------------------


# ------------------------------
# FETCH OS
# ------------------------------
def get_image(path: Path, platform: str) -> str:
    image = ""
    try:
        stdout = tools.grep(path / const.IMAGE_SOL, "Name: entire", True, 15)
        image_lines = stdout.split('\n')
        for line in image_lines:
            if "Version" in line:
                image = line.split()[4][:-1]
                break
        return image
    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch image: {err}")
        return ""


def get_vol(path: Path, platform: str) -> int:
    try:
        stdout = tools.grep(path / const.PARTITION_SOL, "\\B/$", True)
        vol = stdout.strip().split()[-2]
        vol = 100 - int(vol[:-1])
        return vol
    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch volume: {err}")
        return ""


def get_raid(path: Path) -> bool:
    try:
        stdout = tools.grep(path / const.RAID_SOL, "mirror", True)
        raid_stat = "ONLINE" in stdout.strip().split()
        return raid_stat

    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch raid: {err}")
        return False


def get_bonding(path: Path) -> str:
    try:
        net_ipmp = tools.grep(path / const.NETWORK_SOL, "ipmp", True)
        net_aggr = tools.grep(path / const.NETWORK_SOL_AGGR, "up", True)
        if not net_ipmp and not net_aggr:
            bonding = "none"
        elif net_ipmp and not net_aggr:
            state = net_ipmp.split()[2]
            bonding = "ipmp" if state == "ok" else ""
        elif net_aggr and not net_ipmp:
            state = net_aggr.split()[4]
            # if state == "up":
            #     bonding = "aggr"
            bonding = "aggr" if state == "up" else ""
        else:
            bonding = "both"

        return bonding
    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch bonding status: {err}")
        return ""


def get_cpu_util(path: Path) -> (int, int):
    try:
        cpu_util_path = path / const.CPU_ULTILIZATION_SOL
        regex = '*.dat'
        files = sorted(cpu_util_path.glob(regex), reverse=True)
        cpu_idle_alltime = []

        for file in files:
            stdout_lines = tools.grep(
                file, "CPU states:", False)

            cpu_idle_perfile_list = [float(stdout.split()[2][:-1])
                                     for stdout in stdout_lines]

            cpu_idle_perfile = sum(cpu_idle_perfile_list) / \
                len(cpu_idle_perfile_list)
            cpu_idle_alltime.append(cpu_idle_perfile)

        cpu_idle = round(sum(cpu_idle_alltime) / len(cpu_idle_alltime), 2)
        cpu_util = round(100 - cpu_idle, 2)

        return [cpu_util, cpu_idle]
    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch cpu utilization: {err}")
        return [-1, -1]


def get_load_avg(path: Path) -> float:
    try:
        stdout = tools.grep(path / const.CPU_LOAD_SOL, "load average", True)
        load = stdout.strip().split(", ")
        load_avg = float(max(load[-3:], key=float))

        return load_avg
    except (RuntimeError, Exception) as err:
        print(f"FAILED to get load average: {err}")
        return ""


def get_vcpu(path: Path) -> int:
    try:
        stdout = tools.grep(path / const.VCPU_SOL,
                            "Status", single_match=False
                            )
        vcpu = stdout[-1].split()[4]
        vcpu = int(vcpu) + 1

        return vcpu
    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch VCPU: {err}")
        return ""


def get_load(path: Path) -> float:
    try:
        load_avg = get_load_avg(path)
        vcpu = get_vcpu(path)
        load_avg_per = load_avg / vcpu
        load_avg_per = float(f"{load_avg_per:.3f}")

        return load_avg, vcpu, load_avg_per
    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch load: {err}")
        return -1, -1, -1


def get_mem_free(path: Path) -> dict:
    x = {"mem_free_percent": 0,
         "mem_free": 0,
         "total_mem": 0}
    try:
        mem_free_path = path / const.MEM_SOL
        regex = "*.dat"
        files = sorted(mem_free_path.glob(regex), reverse=True)
        # core.logger.debug(map(str, files))

        total_mem = float(tools.grep(
            files[-1], "Memory", True).split()[1][:-1])

        mem_free_alltime = []

        for file in files:
            stdout_lines = tools.grep(
                file, "Memory", False)

            mem_free_perfile_list = [float(stdout.split()[4][:-1])
                                     for stdout in stdout_lines]
            mem_free_perfile = sum(mem_free_perfile_list) / \
                len(mem_free_perfile_list)
            mem_free_alltime.append(mem_free_perfile)

        mem_free = round(sum(mem_free_alltime) / len(mem_free_alltime))

        if mem_free > total_mem:
            mem_free = mem_free / 1024

        mem_free_percent = round((mem_free / total_mem) * 100)
        mem_util_percent = round(100 - mem_free_percent, 2)

        x["mem_free_percent"] = mem_free_percent
        x["mem_free"] = mem_free
        x["total_mem"] = total_mem

        return x
    except RuntimeError:
        return x
    except Exception as err:
        print(f"FAILED to fetch memory util: {err}")
        raise


def get_io_busy(path: Path) -> dict:
    try:
        io_busy_path = path / const.IO_SOL
        regex = "*.dat"
        files = sorted(io_busy_path.glob(regex), reverse=True)

        devices = []
        # Get devices name list
        temp = tools.cat(files[0], True)
        for line in temp[4:]:
            if "zzz" in line:
                break
            devices.append(line.split()[-1])

        average_alltime = [0] * len(devices)
        total_alltime = [0] * len(devices)
        # Evaluation begin
        for file in files:
            stdout = tools.cat(file, True)
            average_perfile = [0] * len(devices)
            total_perfile = [0] * len(devices)

            # Evaluate each section in a file
            # Count the number of value that > 0
            value_count = [1] * len(devices)
            persection_list = [0] * len(devices)

            index = 1
            while index < len(stdout):
                if "zzz" in stdout[index]:
                    if index == 1:
                        index += 3
                        continue
                    try:
                        for i in range(len(persection_list)):
                            total_perfile[i] += persection_list[i]
                            persection_list[i] = 0
                    except Exception as err:
                        core.logger.error(err)
                    index += 3
                    continue

                device_name = stdout[index].split()[-1]
                io_value = float(stdout[index].split()[-2])
                if io_value > 0:
                    persection_list[devices.index(device_name)] = io_value
                    value_count[devices.index(device_name)] += 1
                index += 1

            for i in range(len(devices)):
                average_perfile[i] = total_perfile[i] / value_count[i]
                total_alltime[i] += average_perfile[i]

        average_alltime = [total / len(files) for total in total_alltime]

        sorted_io_busy = sorted(average_alltime, reverse=True)

        return {"name": None, "busy": sorted_io_busy[0]}
    except Exception as err:
        core.logger.error(err)
        core.logger.error("FAILED:fetch io busy")
        return {"name": None, "busy": 0}


def get_swap_util(path: Path):
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
        print("FAILED to get swap util")
        raise


def get_system_status(path: Path, platform: str, server_type: str) -> dict:
    x = {}
    try:
        if platform == "solaris":
            x["image"] = get_image(path, platform)
            x["vol_avail"] = get_vol(path, platform)

            if server_type == "baremetal":
                x["raid_stat"] = get_raid(path)
                x["bonding"] = get_bonding(path)
        elif platform == "linux":
            pass
        elif platform == "exa":
            pass
        else:
            print("FAILED to fetch OS information")
            raise RuntimeError()

    except RuntimeError:
        print("FAILED to fetch OS information")
        raise

    return x


def get_system_perform(path: Path, platform: str, system_type: str) -> dict:
    x = {}
    try:
        if system_type == "standalone":
            if platform == "solaris":
                x["cpu_util"] = get_cpu_util(path)[0]
                x["mem_free"] = get_mem_free(path)
                x["io_busy"] = get_io_busy(path)
            elif platform == "linux":
                # load = get_load(path)
                # x["load"] = {}
                # x["load"]["load_avg"] = load[0]
                # x["load"]["vcpu"] = load[1]
                # x["load"]["load_avg_per"] = load[2]
                # filler
                # x["io_busy"] = ""

                # swap_util = get_swap_util(path)[1]
                # x["swap_util"] = swap_util
                pass
        elif system_type == "exa":
            pass

    except RuntimeError as err:
        core.logger.error(f"FAILED to fetch OS information: {err}")
        raise

    return x
# ------------------------------
# END FETCH OS
# ------------------------------


def get_detail(
        node: str, list_logs_dir: list, node_dir: Path, system_info: dict
) -> dict:
    # ilom = {}
    # system_status = {}
    # system_perform = {}
    ilom = {"fault": "", "inlet": "", "exhaust": "", "firmware": ""}
    system_status = {"image": "", "vol_avail": "",
                     "raid_stat": "", "bonding": ""}
    system_perform = {"cpu_util": "", "mem_free": "",
                      "io_busy": {"name": "", "busy": ""}}

    for subdir in ["ilom", "status", "perform"]:
        create_dir(node_dir / subdir)

    core.logger.debug(
        "PATH: " + json.dumps(list(map(str, list_logs_dir)), indent=2))

    try:
        if system_info["type"] == "baremetal":
            ilom.update(get_ilom(list_logs_dir[0], system_info)
                        if list_logs_dir[0] else {})
        # OSWatcher
        if system_info["system_type"] in ["standalone", "exa"]:
            if list_logs_dir[1]:
                system_status.update(get_system_status(list_logs_dir[1],
                                                       system_info["platform"],
                                                       system_info["type"]))
            if list_logs_dir[2]:
                system_perform.update(
                    get_system_perform(list_logs_dir[2],
                                       system_info["platform"],
                                       system_info["system_type"]))
    except RuntimeError as err:
        core.logger.error(err)
        raise
    name = node

    content = {"node_name": name,
               **ilom,
               **system_status,
               **system_perform}
    core.logger.info("FETCHED: " +
                     json.dumps(content,
                                indent=2,
                                ensure_ascii=False))
    # Save information
    tools.save_json(node_dir / "ilom" / "ilom.json", ilom)
    tools.save_json(node_dir / "status" / "status.json", system_status)
    tools.save_json(node_dir / "perform" / "perform.json", system_perform)

    return [content]


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


def compile(
        nodes_name: list, list_file_logs: list,
        system_info: dict, out_dir: Path, force: bool
) -> list:
    content_files = []
    print("CHOOSE FILE TO EXTRACT")

    print("-----------------------------")
    for node in nodes_name:
        node_dir = Path(out_dir) / node
        print(f"FETCHING:{node}")
        list_logs_dir = [None, None, None]
        print("RUNNING:EXTRACT FILES")
        file_logs = list_file_logs[nodes_name.index(node)]
        extraction_formats = ["ILOM SNAPSHOT", "EXPLORER", "OSWATCHER"]
        exclude = ["./rda/", "./cluster/", "./samfs/",
                   "./ldom/core", "./fma/var", "./patch+pkg/pkg_contents.out",
                   "./ldom/opt/", "./messages/", "./var/svc/",
                   "./sp_snapshot/", "./ldom/log/",
                   ]
        for i, file_type in enumerate(["zip", "tar.gz", "gz"]):
            try:
                print(f"RUNNING:EXTRACT {extraction_formats[i]}")
                list_logs_dir[i] = extract_file(
                    file_logs[i], file_type, force, exclude=exclude)
            except ValueError as err:
                core.logger.error(err)

        content_files.append(node_dir / f"{node}.json")

        list_logs_dir = [Path(f"temp/{logs_dir}/")
                         if logs_dir != Path("temp") else Path("")
                         for logs_dir in list_logs_dir]
        core.logger.info(json.dumps(list(map(str, list_logs_dir)), indent=2))

        try:
            print("RUNNING:GET DETAILS")
            content = get_detail(node, list_logs_dir, node_dir, system_info)
            print("RUNNING:DRAW IMAGES")
            images = drw_content(list_logs_dir, node_dir, system_info)
            print("RUNNING:SAVE IMAGES")
            # Save image names
            tools.save_json(node_dir / "images.json", images)
            # Save information
            tools.save_json(node_dir / f"{node}.json", content)
            print("DONE")
            print()
        except RuntimeError:
            raise
    sys.stdout.write("\033[?25h")
    return content_files


def create_dir(
        path: Path, parents: bool = False,
        exist_ok: bool = False, force: bool = False
) -> None:
    try:
        Path.mkdir(path, parents=parents, exist_ok=exist_ok)
        core.logger.info("FOLDER CREATED: " + str(path))
    except FileExistsError:
        if not path.iterdir():
            return
        if force:
            clean_up(
                path=os.path.normpath(path),
                prompt="Do you want to replace it?",
                force=force,
            )
        else:
            print(str(path) + " folder exist!")
            clean_up(
                path=os.path.normpath(path),
                prompt="Do you want to replace it?",
                force=force,
            )


def set_system_info():
    """
    Set system Information with following field.
    Get info from user stdin.
1. TYPES:  "baremetal"  -- Physical
           "vm"         -- Virtual Machine
2. SYSTEM: "standalone" -- Single Machine System
           "exa"        -- Engineered System
3. PLATFORM: "linux"    -- Oracle Linux
             "solaris"  -- Oracle Solaris
    """
    def prompt_user(prompt, default):
        while True:
            try:
                user_input = str(input(f"{prompt}\n [{default}] ") or default)
                if user_input in [default, "standalone", "exa", "linux",
                                  "solaris", "baremetal", "vm"]:
                    return user_input
            except KeyboardInterrupt:
                print()
                sys.exit()

    system_info = {}
    system_info["system_type"] = prompt_user(
        "System Type [standalone|exa]?", "standalone")
    system_info["platform"] = prompt_user(
        "Platform [linux|solaris]?", "solaris")
    system_info["type"] = prompt_user("Type [baremetal|vm]?", "baremetal")

    print(json.dumps(system_info, indent=2))

    return system_info

# Flow of program


def run(
        logs_dir: Path, out_dir: Path, force: bool
) -> str:
    """
    Initialize the fetch process.

    Get client name, make necessary directories,
    let user choose log files and fetch data.

    Parameters
    ----------
    logs_dir : str
            Directory to the Logs input.
    out_dir : str
            Directory to the output.
    force : bool
            Force flag option.
    """
    if not os.path.isfile("/usr/share/java/oswbba.jar"):
        print("oswbba.jar - oswatcher generator not found! in /usr/share/java")
        print("Please install it.")
        sys.exit()
    # Take client/customer name
    client = input("Enter client name: ")
    out_dir = Path(out_dir) / client
    # Root folder initialization
    root_dir = out_dir / datetime.datetime.utcnow().strftime('%Y-%m-%dT%H%M%S')
    # Create necessary directories
    create_dir(Path("temp"), parents=True, exist_ok=True)
    create_dir(out_dir, parents=True, exist_ok=True)
    create_dir(root_dir)

    i = 0
    list_alltime_logs = []
    summary_list = []
    nodes_list = []
    system_info_list = []

    out_file = root_dir / "summary.json"

    while True:
        system_info = set_system_info()
        system_info["client"] = client
        system_info_list.append(system_info)
        nodes_name = input(
            "Enter nodes' name (each separated by a space): ").split(" ")
        nodes_list.append(nodes_name)

        list_file_logs = []
        for node in nodes_name:
            create_dir(root_dir / node, force=force)
            try:
                file_logs = ["", "", ""]
                print("NODE:" + node)
                print("-----------------------------")
                print("ILOM SNAPSHOT")
                file_logs[0] = get_file("**/*.zip", logs_dir)
                print("EXPLORER")
                file_logs[1] = get_file("**/*.tar.gz", logs_dir)
                print("OSWATCHER")
                file_logs[2] = get_file("**/*.gz", logs_dir)

                list_file_logs.append(file_logs)
                print()
            except RuntimeError as err:
                err.add_note("Data files must be exist!")
                raise err

        out_file_part = root_dir / f"summary-{i}.json"
        tools.save_json(out_file_part, system_info)
        summary_list.append(out_file_part)
        list_alltime_logs.append(list_file_logs)
        i += 1
        c = input("Run another time?[Y/N] ")
        if c in ["", "Y", "y", "yes", "Yes", "YES"]:
            continue
        else:
            break

    summary_content = []
    for time in range(0, i):
        try:
            content_files = compile(
                nodes_list[time], list_alltime_logs[time],
                system_info_list[time], root_dir, force)

            core.logger.info(content_files)
        except RuntimeError:
            print("Aborted")
            raise
        tools.join_json(summary_list[time], content_files)
        summary_content.append(tools.read_json(summary_list[time]))

    tools.save_json(out_file, summary_content)

    # Union all jsons to one file
    return out_file


# ------------------------------
# MAIN
# ------------------------------
def main():
    """
    pass
    """
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
