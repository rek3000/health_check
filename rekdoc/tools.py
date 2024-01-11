import json
import logging
import click
import os
import subprocess
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


##### JSON #####
# get a dictionary as input and dump it to a json type file
def save_json(file, content, append=True):
    if not content:
        click.echo("No content from input to save!")
        return -1
    try:
        if append:
            with open(file, "a+") as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
        else:
            with open(file, "w+") as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
    except OSError as err:
        logging.error("OS error: ", err)
        raise RuntimeError("Cannot save JSON") from err


def read_json(file):
    try:
        with open(file, "r+") as f:
            content = json.load(f)
            return content
    except FileNotFoundError as err:
        raise RuntimeError("JSON file must be exist") from err
    except ValueError as err:
        raise RuntimeError("Cannot read JSON file") from err
    # except Exception as err:
    #     print(err)


def join_json(out_file, content_files):
    file_data = {}
    try:
        try:
            file_data = read_json(out_file)
        except Exception as err:
            print(err)
            file_data = {}
        logging.info(json.dumps(file_data, indent=2))
        with open(out_file, "a+") as file:
            file_data["nodes"] = []
            # logging.info(json.dumps(file_data, indent=2))
            for content in content_files:
                logging.info(json.dumps(content, indent=2))
                buffer = read_json(content)
                file_data["nodes"].append(buffer)
            json.dump(file_data, file, indent=4, ensure_ascii=False)

    except OSError as err:
        logging.error("OS error: ", err)
        raise RuntimeError("Cannot write contents to JSON file") from err


##### END JSON #####


def save_file(file, content):
    try:
        with open(file, "w") as f:
            f.write(content)
    except OSError as err:
        logging.error("OS error: ", err)
        raise RuntimeError("Cannot save file: ") from err


def rm_ext(file, ext):
    return file[: -(len(ext) + 1)]


##### IMAGE GENERATE METHOD #####
# transform text to a png image file
def drw_text_image(text, file):
    size = 16
    try:
        font = ImageFont.truetype(
            "Serif", size=size, layout_engine=ImageFont.Layout.BASIC
        )
    except OSError:
        font = ImageFont.load_default(size)
    except Exception:
        font = ImageFont.load_default()
    with Image.new("RGB", (2000, 2000)) as img:
        d1 = ImageDraw.Draw(img)
        d1.fontmode = "RGB"
        box = d1.textbbox((10, 10), text.getvalue(), font=font)
        right, bottom = box[-2], box[-1]
        w = int(right * 1.1) + 5
        h = int(bottom * 1.1) + 5
        # img_resize = img.resize((w, h), resample=Image.LANCZOS)
        img_resize = img.crop((0, 0, w, h))
        d2 = ImageDraw.Draw(img_resize)
        d1.fontmode = "RGB"
        x = 10
        y = 10
        box = font.getbbox(text.getvalue())
        bottom = box[-1]
        attSpacing = bottom
        for line in text.getvalue().split("\n"):
            d2.text((x, y), line.lstrip("\r").rstrip(" \r"), font=font)
            y = y + attSpacing
        img_resize.save(file, format="PNG")


##### END OF IMAGE #####


##### BASE ######
def run(command, tokenize):
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as err:
        click.echo()
        click.echo("Command not found: " + command[0])
        raise RuntimeError(err)
    stdout_stream, stderr_stream = process.communicate()
    returncode = process.wait()

    if not isinstance(stdout_stream, str):
        stdout_stream = str(stdout_stream, "utf-8")
    if not isinstance(stderr_stream, str):
        stderr_stream = str(stderr_stream, "utf-8")

    stdout = None
    stderr = None
    if tokenize:
        stdout = stdout_stream.splitlines()
        stderr = stderr_stream.splitlines()
    else:
        stdout = stdout_stream
        stderr = stderr_stream
    return stdout, stderr, returncode


def cat(file, tokenize=False):
    try:
        command = ["cat", file]
        stdout = run(command, tokenize)[0]
    except RuntimeError:
        click.echo("Cannot cat file: " + file)
        raise
    logging.debug(json.dumps(stdout, indent=2))
    return stdout


def grep(path, regex, single_match, next=0):
    command = ["grep", "-e", regex, "--no-group-separator"]

    if single_match:
        command.extend(["-m1"])
        command.extend(["-A", str(next)])
    else:
        command.extend(["-A", str(next)])
    command.extend([path])

    tokenize = bool(1 - single_match)
    stdout = run(command, tokenize)[0]

    logging.debug(json.dumps(stdout, indent=2))
    return stdout


##### END BASE #####
