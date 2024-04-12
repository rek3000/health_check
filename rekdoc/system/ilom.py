import json
import io
from pathlib import Path

from rekdoc import core
from rekdoc import tools
from rekdoc import const


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


def drw_ilom(path: Path, out_dir: Path, system_info: dict) -> list:
    drw_fault(path, out_dir, system_info)
    drw_temp(path, out_dir)
    drw_firmware(path, out_dir)
    return ["ilom/fault.png", "ilom/temp.png", "ilom/firmware.png"]


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


def get_fault(path: Path, type: str) -> str:
    fault = ""

    try:
        if type == "vm":
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


def get_ilom(path: Path, system_info: dict) -> dict:
    if not path.is_dir():
        return {"fault": "", "inlet": "", "exhaust": "", "firmware": ""}
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
