import io
import shutil
# import json
from pathlib import Path

from rekdoc import core
from rekdoc import tools
from rekdoc import const


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


def get_image(path: Path) -> str:
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


def get_vol(path: Path) -> int:
    try:
        stdout = tools.grep(path / const.PARTITION_SOL, "\\B/$", True)
        vol = stdout.strip().split()[-2]
        vol = 100 - int(vol[:-1])
        return vol
    except (RuntimeError, Exception) as err:
        print(f"FAILED to fetch volume: {err}")
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


def get_system_status(path: Path, type: str) -> dict:
    x = {}
    if not path.is_dir():
        return x
    try:
        x["image"] = get_image(path)
        x["vol_avail"] = get_vol(path)
        if type == "baremetal":
            x["raid_stat"] = get_raid(path)
            x["bonding"] = get_bonding(path)
    except RuntimeError:
        print("SOLARIS:FAILED to fetch System Status")
        raise

    return x


def get_system_perform(path: Path) -> dict:
    x = {}
    if not path.is_dir():
        return x
    try:
        x["cpu_util"] = get_cpu_util(path)[0]
        x["mem_free"] = get_mem_free(path)
        x["io_busy"] = get_io_busy(path)
    except RuntimeError as err:
        core.logger.error(f"SOLARIS:FAILED to fetch System Performance: {err}")
        raise

    return x


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


def drw_system_status(path: Path, out_dir: Path, type: str) -> list:
    """
    Draw System Status Images (Explorer) from Extracted Logs

    path : Path
        Path to the log directory.
    out_dir : Path
        Path to the output directory.
    system_info: dict
        System Information of the machine.
    """
    if not path.is_dir():
        return ["",
                ["", ""],
                "", ]
    if type == "baremetal":
        drw_image(path, out_dir)
        drw_vol(path, out_dir)
        drw_raid(path, out_dir)
        drw_net(path, out_dir)
        return [
            "status/image.png",
            ["status/vol.png", "status/raid.png"],
            "status/net.png",
        ]
    elif type == "vm":
        drw_image(path, out_dir)
        drw_vol(path, out_dir)
        return [
            "status/image.png",
            ["status/vol.png", ""],
        ]


def drw_system_performance(
        path: Path, out_dir: Path
) -> list:
    """Draw System Performance Images (OSWatcher) from Extracted Logs
Clarification: This just run the oswbba.jar file and
generate images from OSWatcher.

    path : Path
        Path to the log directory.
    out_dir : Path
        Path to the output directory.
    system_info: dict
        System Information of the machine.
    """
    if not path.is_dir():
        return ["", "", ""]
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
