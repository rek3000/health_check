"""**SYSTEM DATA FETCHER**

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

# Local library
from rekdoc import core
from rekdoc import tools
from rekdoc import const
from rekdoc.system import solaris
from rekdoc.system import ilom


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
    """Extract Files with filter (exclude list).

    file : Path
        Path to the compressed file.
    compress : str
        Compress type. Support "tar.gz", "gz" and "zip" files.
    exclude : list
        Excluded files and directories list
        , not included in extraction/decompression.
    force : bool
        True = replace the output directory.
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

    file: Path
        Path to the compressed file.
    exclude : list
        Excluded files and directories list
        , not included in extraction/decompression.
    force : bool
        True = replace the output directory.
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
                    raise

    except IOError as err:
        core.logger.error(err)
        raise


def untar(file: Path, compress: str, force: bool, exclude: list | None = None):
    """
    Helper function to decompress tar file with filter.

    file: Path
        Path to the compressed file.
    exclude : list
        Excluded files and directories list
        , not included in extraction/decompression.
    force : bool
        True = replace the output directory.
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
                    raise

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


# Find the file matched with keyword(regular expression)
def get_file(regex: str, logs_dir: Path) -> Path:
    """Choose a file from list of files
Print a list of files in the 'dir' and let user choose file through number.

    regex : str
        Regular expression string.
    logs_dir : Path
        Path to log directory
    """
    # core.logger.debug(str(logs_dir))

    def print_files(files: list):
        for i, file in enumerate(files):
            print(f"[{i}] {file.name}")
        print("[-1] Skip")

    def get_user_input(files: list):
        while True:
            try:
                choice = int(
                    input("Which file?\n [0] [Ctrl-C to reselect this node]") or "0")
                if choice == -1 or (0 <= choice < len(files)):
                    return choice
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except ValueError:
                continue

    files = sorted(logs_dir.glob(regex), reverse=True)

    try:
        print_files(files)
    except Exception:
        return ""
    try:
        choice = get_user_input(files)
    except KeyboardInterrupt:
        raise KeyboardInterrupt

    if choice == -1:
        return ""
    else:
        return files[choice]


def check_valid(path):
    return os.path.isdir(path)
# ------------------------------
# END HELPER
# ------------------------------


# ------------------------------
# IMAGE PROCESSING
# ------------------------------
# DRAW
def drw_swap(path: Path, out_dir: Path) -> str:
    swap = io.StringIO()
    swap.write(str(path) + "/" + const.SWAP_SOL + "\n")
    swap.write(tools.cat(path / const.SWAP_SOL))
    tools.drw_text_image(swap, out_dir / "swap.png")
    return swap


def drw_content(path: Path, out_dir: Path, system_info: dict) -> list:
    ilom_image = []
    if system_info["type"] == "baremetal":
        ilom_image = ilom.drw_ilom(path[0], out_dir / "ilom", system_info)
    else:
        ilom.drw_fault(path[1], out_dir / "ilom", system_info)
        ilom_image = ["ilom/fault.png"]
    system_status = solaris.drw_system_status(
        path[1], out_dir / "status", system_info["type"])
    system_performance = solaris.drw_system_performance(
        path[2], out_dir / "perform")
    images = ilom_image + system_status + system_performance
    core.logger.info(images)
    return images


# ------------------------------
# FETCH ILOM
# ------------------------------
# ------------------------------
# END FETCH ILOM
# ------------------------------


# ------------------------------
# FETCH OS
# ------------------------------
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

# ------------------------------
# END FETCH OS
# ------------------------------


def get_detail(
        node: str, list_logs_dir: list, node_dir: Path, system_info: dict
) -> dict:
    """
    node : str
        Node name to get details.
    list_logs_dir : list
        List of logs directories.
    node_dir : Path
        Path to the node output directory.
    system_info : dict
        System Information of the machine.

    """
    # ilom = {}
    # system_status = {}
    # system_perform = {}
    ilom_status = {"fault": "", "inlet": "", "exhaust": "", "firmware": ""}
    system_status = {"image": "", "vol_avail": "",
                     "raid_stat": "", "bonding": ""}
    system_perform = {"cpu_util": "", "mem_free": "",
                      "io_busy": {"name": "", "busy": ""}}

    for subdir in ["ilom", "status", "perform"]:
        tools.create_dir(node_dir / subdir)

    core.logger.debug(
        "PATH: " + json.dumps(list(map(str, list_logs_dir)), indent=2))

    try:
        if system_info["type"] == "baremetal":
            ilom_status.update(ilom.get_ilom(list_logs_dir[0], system_info)
                               if list_logs_dir[0] else {})
        elif system_info["type"] == "vm":
            ilom_status.update(ilom.get_fault(
                list_logs_dir[1], system_info["type"]))
        # OSWatcher
        # if system_info["system_type"] in ["standalone", "exa"]:
        if system_info["platform"] == "solaris":
            if list_logs_dir[1]:
                system_status.update(
                    solaris.get_system_status(
                        list_logs_dir[1], system_info["type"]))
            if list_logs_dir[2]:
                system_perform.update(
                    solaris.get_system_perform(list_logs_dir[2]))
    except RuntimeError as err:
        core.logger.error(err)
        raise
    name = node

    content = {"node_name": name,
               **ilom_status,
               **system_status,
               **system_perform}
    core.logger.info("FETCHED: " +
                     json.dumps(content,
                                indent=2,
                                ensure_ascii=False))
    # Save information
    tools.save_json(node_dir / "ilom" / "ilom.json", ilom_status)
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


def set_system_info():
    """Set system Information with following field.
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

    logs_dir : Path
            Directory to the Logs input.
    out_dir : Path
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
    tools.create_dir(Path("temp"), parents=True, exist_ok=True)
    tools.create_dir(out_dir, parents=True, exist_ok=True)
    tools.create_dir(root_dir)

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
            tools.create_dir(root_dir / node, force=force)
            try:
                file_logs = ["", "", ""]
                print("NODE:" + node)
                print("-----------------------------")
                while True:
                    print("ILOM SNAPSHOT")
                    try:
                        file_logs[0] = get_file("**/*.zip", logs_dir)
                        break
                    except KeyboardInterrupt:
                        print()
                        continue

                while True:
                    print("EXPLORER")
                    try:
                        file_logs[1] = get_file("**/*.tar.gz", logs_dir)
                        break
                    except KeyboardInterrupt:
                        print()
                        continue

                while True:
                    print("OSWATCHER")
                    try:
                        file_logs[2] = get_file("**/*.gz", logs_dir)
                        break
                    except KeyboardInterrupt:
                        print()
                        continue

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
# def main():
#     """
#     pass
#     """
#     print("------------------------------")
#     print("RUNNING AS A STANDALONE MODULE")
#     print("------------------------------")
#
#     data_object = {
#         "nodes_name": ["DBMC01", "DBMC02", "DBMC-DR"],
#         "logs_dir": "./sample/",
#         "output_file": "output/solaris.json",
#         "force": False,
#     }
#
#     run(
#         nodes_name=data_object["nodes_name"],
#         logs_dir=data_object["logs_dir"],
#         output_file=data_object["output_file"],
#         force=data_object["force"],
#     )


# if __name__ == "__main__":
    # main()
# ****************************************
# END MAIN
# ****************************************
