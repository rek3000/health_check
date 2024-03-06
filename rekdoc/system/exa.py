import io
import shutil
# import json
from pathlib import Path

from rekdoc import core
from rekdoc import tools
from rekdoc import const


def get_image(path: Path) -> str:
    pass


def get_raid(path: Path) -> str:
    pass


def get_vol(path: Path) -> int:
    pass


def get_bonding(path: Path) -> bool:
    pass


def get_system_status(path: Path) -> dict:
    x = {}
    try:
        x["image"] = get_image(path)
        x["vol_avail"] = get_vol(path)
        x["raid_stat"] = get_raid(path)
        x["bonding"] = get_bonding(path)
    except RuntimeError:
        print("EXADATA:FAILED to fetch System Status")
        raise
    return x


def get_cpu_util(path: Path) -> (int, int):
    pass


def get_load_avg(path: Path) -> float:
    pass


def get_vcpu(path: Path) -> int:
    pass


def get_load(path: Path) -> (float, int, float):
    pass


def get_mem_free(path: Path) -> dict:
    pass


def get_swap_util(path: Path) -> dict:
    pass


def get_flash_io(path: Path) -> float:
    pass


def get_flash_bandwidth(path: Path) -> float:
    pass


def get_hard_disk_io(path: Path) -> float:
    pass


def get_hard_disk_bandwidth(path: Path) -> float:
    pass


def get_system_performance(path: Path, db: bool) -> dict:
    x = {}
    try:
        x["cpu_util"] = get_cpu_util(path)
        if db:
            x["load_avg"] = get_load(path)
            x["mem_free"] = get_mem_free(path)
            x["swap_util"] = get_swap_util(path)
        else:
            x["flash_io"] = get_flash_io(path)
            x["flash_bandwidth"] = get_flash_bandwidth(path)
            x["hard_disk_io"] = get_hard_disk_io(path)
            x["hard_disk_bandwidth"] = get_hard_disk_bandwidth(path)
    except RuntimeError:
        print("EXADATA:FAILED to fetch System Performance")
        raise

    return x
