import json
import sys, re, io, os
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from textwrap import wrap

##### JSON #####
#get a dictionary as input and dump it to a json type file
def save_json(file, content):
    if not content:
        print('No content from input to save!')
        return -1
    try:
        with open(file, 'w') as f:
            json.dump(content, f, indent=2)
    except OSError as err:
        print('OS error: ', err)
        raise RuntimeError('Cannot save JSON') from err
        return -1

def read_json(file):
    try:
        with open(file, 'r') as f:
            content = json.load(f)
        return content
    except FileNotFoundError as err:
        raise RuntimeError('Input file not found!') from err
        return -1
    except OSError as err:
        raise RuntimeError('Cannot read JSON') from err
        return -1

def join_json(content_files, output):
    try:
        with open(output, 'w+') as file:
            x = {}
            for i in content_files:
                path = './output/' + i.split('.')[0]
                path = os.path.normpath(''.join(path).split('_')[0]  + '/' + i + '.json')
                buffer = read_json(path)
                key = list(buffer)[0]
                x[key] = buffer[key]
            json.dump(x, file, indent=4)
    except OSError as err:
        print('OS error: ', err)
        return -1

##### END JSON #####

def save_file(file, content):
    try:
        with open(file, 'w') as f:
            f.write(content)
    except OSError as err:
        raise RuntimeError('Cannot save file: ') from err
        return -1

def rm_ext(file, ext):
    return file[:-len(ext)-1]

##### IMAGEMAGICK #####
# transform text to a png image file 
def drw_text_image(text, file):
    with Image(width=1000, height=1000, background=Color('black')) as img:
        img.format = 'png'
        with Drawing() as context:
            tmp = text.getvalue()
            metrics = context.get_font_metrics(img, tmp, True)
            x = 10
            y = 14
            w = int(metrics.text_width*1.2)
            h = int(metrics.text_height*1.3)
            img.resize(w, h)
            context.font_family = 'monospace'
            context.font_size = y
            context.fill_color = Color('white')
            context.gravity = 'north_west'
            context.text_antialias = True
            context.text(x, y, text.getvalue())
            context(img)
        img.save(filename='PNG24:' + file)
##### END OF IMAGEMAGICK #####

##### BASE ######
# TODO: REWRITE IN STRINGIO
def cat(path, stdout=True, debug=False):
    try:
        with open(path, 'r') as file:
            content = file.readlines()
            if stdout:
                count = 0
                result = ''
                for l in content:
                    result += l.lstrip()
                    count += 1
                    if debug:
                        print(count + 1, ': ', l, sep='', end='')
                return result
            else: 
                result = io.StringIO()
                count = 0
                for l in content:
                    result.write(l)
                    count += 1
                    if debug:
                        print(count + 1, ': ', l, sep='', end='')
                return result
    except Exception as err:
        raise RuntimeError('Cannot open file to read') from err
        return -1

# return the matched line along with next `n` lines
# not so optimized but usable
def cursed_grep(path, regex, number=0, debug=False):
    result = io.StringIO()
    # call grep() then get line number returned
    line_number = int(grep(path, regex, True, True, debug=debug).split()[0][:-1])
    with open(path, 'r') as f:
        lines = f.readlines()[line_number-1:]
        for i in range(number):
            result.write(lines[i])
    return result

# TODO: remake using StringIO
def grep(path, regex, single_line=True, print_line=False, debug=False):
    result = ''
    flag = re.MULTILINE
    pattern = re.compile(regex, flag)
    file = cat(os.path.normpath(path), False)
    content = file.getvalue().split('\n')

    if single_line:
        for line in range(len(content)):
            if re.search(pattern, content[line]):
                result += content[line].lstrip()
                if print_line:
                    result = str(line + 1) + ': ' + result
                break 
    else:
        for line in range(len(content)):
            if re.search(pattern, content[line]):
                result += content[line].lstrip()
                if print_line:
                    result = str(line + 1) + ': ' + result
    if debug:
        print(result)
        print()
    return result
##### END BASE #####
