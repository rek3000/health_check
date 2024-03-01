import json
import subprocess
from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from rekdoc import core


##### JSON #####
# get a dictionary as input and dump it to a json type file
def save_json(file: Path, content: str, append: bool = True) -> None:
    if not content:
        print("No content from input to save!")
        return -1

    mode = "a+" if append else "w+"

    try:
        with file.open(mode=mode) as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
    except OSError as err:
        core.logger.error(f"OS error: {err}")
        raise RuntimeError("Cannot save JSON file") from err


def read_json(file: Path) -> str:
    try:
        with file.open(mode="r+") as f:
            content = json.load(f)
            return content
    except FileNotFoundError as err:
        raise RuntimeError("JSON file must exist") from err
    except ValueError as err:
        raise RuntimeError("Cannot read JSON file") from err


def join_json(out_file: Path, content_files: list) -> None:
    try:
        file_data = {}
        try:
            file_data = read_json(out_file)
        except Exception as err:
            core.logger.debug(f"Error reading existing JSON file: {err}")

        with out_file.open(mode="w+") as file:
            file_data["nodes"] = []

            for content in content_files:
                try:
                    # core.logger.info(json.dumps(content, indent=2))
                    buffer = read_json(content)[0]
                    file_data["nodes"].append(buffer)
                except Exception as err:
                    core.logger.error(
                        f"Error reading JSON content file: {err}")

            json.dump(file_data, file, indent=4, ensure_ascii=False)

    except OSError as err:
        core.logger.error("OS error: ", err)
        raise RuntimeError("Cannot write contents to JSON file") from err
##### END JSON #####


# def save_file(file, content):
#     try:
#         with open(file, "w") as f:
#             f.write(content)
#     except OSError as err:
#         core.logger.error("OS error: ", err)
#         raise RuntimeError("Cannot save file: ") from err


def rm_ext(name: str, ext: str) -> str:
    return name[: -(len(ext) + 1)]


##### IMAGE GENERATE METHOD #####
# transform text to a png image file
def drw_text_image(text: str | list, file: Path) -> None:
    size = 12
    try:
        font = ImageFont.truetype(
            "monospace", size=size, layout_engine=ImageFont.Layout.BASIC
        )
    except OSError:
        font = ImageFont.load_default(size)
    except Exception:
        font = ImageFont.load_default()

    text = text.getvalue().replace('\t', '  ')

    core.logger.debug(f"DRAWING:{text}")
    with Image.new("RGB", (2000, 2000), color=(19, 20, 22)) as img:
        d1 = ImageDraw.Draw(img)
        d1.fontmode = "RGB"
        box = d1.textbbox((10, 10), text, font=font)
        right, bottom = box[-2], box[-1]
        w = int(right * 1.2) + 5
        h = int(bottom * 1.2) + 5

        # img_resize = img.resize((w, h), resample=Image.LANCZOS)
        img_resize = img.crop((0, 0, w, h))
        d2 = ImageDraw.Draw(img_resize)
        d1.fontmode = "RGB"

        x = 10
        y = 10
        box = font.getbbox(text)
        bottom = box[-1]
        attSpacing = bottom
        for line in text.split("\n"):
            d2.text((x, y), line.lstrip("\r").rstrip(" \r"), font=font)
            y += attSpacing

        img_resize.save(str(file), format="PNG")


##### END OF IMAGE #####


##### BASE ######
def run(command: str, tokenize: bool) -> (str, str, int):
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as err:
        print(f"Command not found: {command[0]}")
        raise RuntimeError(err)

    stdout, stderr = process.communicate()
    returncode = process.returncode

    if tokenize:
        stdout = stdout.splitlines()
        stderr = stderr.splitlines()

    return stdout, stderr, returncode


def cat(file: Path, tokenize: bool = False) -> list | str:
    try:
        command = ["cat", str(file)]
        stdout = run(command, tokenize)[0]
    except RuntimeError:
        print("Cannot cat file: " + str(file))
        raise
    # core.logger.debug(json.dumps(stdout, indent=2))
    return stdout


def grep(path: Path, regex: str, single_match: bool, next: int = 0) -> list | str:
    core.logger.debug("GREP FILE: " + str(path))
    command = ["grep", "-e", regex, "--no-group-separator"]

    if single_match:
        command.extend(["-m1"])
        command.extend(["-A", str(next)])
    else:
        command.extend(["-A", str(next)])
    command.extend([str(path)])

    tokenize = not single_match
    stdout = run(command, tokenize)[0]

    # core.logger.debug(json.dumps(stdout, indent=2))
    return stdout


##### END BASE #####
