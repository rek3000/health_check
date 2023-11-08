import json
import sys, re, io, os, subprocess
# from wand.image import Image
# from wand.drawing import Drawing
# from wand.color import Color
from textwrap import wrap
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont


##### JSON #####
# get a dictionary as input and dump it to a json type file
def save_json(file, content):
    if not content:
        print("No content from input to save!")
        return -1
    try:
        with open(file, "w") as f:
            json.dump(content, f, indent=2)
    except OSError as err:
        print("OS error: ", err)
        raise RuntimeError("Cannot save JSON") from err
        return -1


def read_json(file):
    try:
        with open(file, "r") as f:
            content = json.load(f)
        return content
    except FileNotFoundError as err:
        raise RuntimeError("Input file not found!") from err
        return -1
    except ValueError as err:
        print('Invalid JSON file')
        return -1


def join_json(content_files, output):
    try:
        with open(output, "w+") as file:
            x = {}
            for i in content_files:
                path = "./output/" + i.split(".")[0]
                path = os.path.normpath("".join(path).split("_")[0] + "/" + i + ".json")
                buffer = read_json(path)
                key = list(buffer)[0]
                x[key] = buffer[key]
            json.dump(x, file, indent=4)
    except OSError as err:
        print("OS error: ", err)
        return -1


##### END JSON #####


def save_file(file, content):
    try:
        with open(file, "w") as f:
            f.write(content)
    except OSError as err:
        raise RuntimeError("Cannot save file: ") from err
        return -1


def rm_ext(file, ext):
    return file[: -len(ext) - 1]


##### IMAGE GENERATE METHOD #####
# transform text to a png image file
def drw_text_image(text, file):
    size = 14
    try:
        font = ImageFont.truetype('DejaVuSansMono', size=size, layour_engine=ImageFont.Layout.BASIC)
    except:
        font = ImageFont.load_default(size)
    with Image.new("RGB", (1000, 1000)) as img:
        d1 = ImageDraw.Draw(img)
        left, top , right, bottom = d1.textbbox((10,10), text.getvalue(), font=font)
        w = int(right * 1.1) + 10
        h = int(bottom * 1.1) + 10
        img_resize = img.crop((0, 0, w, h))
        d2 = ImageDraw.Draw(img_resize)
        x = 10
        y = 10
        left, top , right, bottom = font.getbbox(text.getvalue())
        attSpacing = bottom
        for line in text.getvalue().split('\n'):
            d2.text((x, y), line.strip('\r'), font=font)
            y = y + attSpacing
        img_resize.save(file, format='PNG')

##### END OF IMAGE #####


##### BASE ######
def run(command, tokenize):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_stream, stderr_stream = process.communicate()
    returncode = process.wait()

    if not isinstance(stdout_stream, str):
        stdout_stream = stdout_stream.decode("utf-8")
    if not isinstance(stderr_stream, str):
        stderr_stream = stderr_stream.decode("utf-8")

    if tokenize:
        stdout = stdout_stream.splitlines()
        stderr = stderr_stream.splitlines()
    else:
        stdout = stdout_stream
        stderr = stderr_stream

    return stdout, stderr, returncode


def cat(file, stdout=False, debug=False):
    command = ["cat", file]
    stdout, stderr, code = run(command, False)
    return stdout


def grep(path, regex, single_match, next=0, debug=False):
    command = ["grep", "-e", regex]

    if single_match:
        command.extend(["-m1"])
        command.extend(["-A", str(next)])
    else:
        command.extend(["-A", str(next)])
    command.extend([path])

    stdout, stderr, code = run(command, False)

    return stdout
##### END BASE #####
