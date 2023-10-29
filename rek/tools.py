import json
import re, io
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
        with open(file + '.json', 'w') as f:
            json.dump(content, f, indent=2)
    except OSError as err:
        print('OS error: ', err)
        raise RuntimeError('Cannot save JSON') from err
        return -1

def read_json(file):
    try:
        with open(file, 'r+') as f:
            content = json.load(f)
        return content
    except OSError as err:
        print('OS error: ', err)
        raise RuntimeError('Cannot read JSON') from err
        return -1

def join_json(content_files, output):
    try:
        with open(output + '.json', 'a+') as file:
            x = {}
            for i in content_files:
                print(i)
                path = './output/' + i.split('.')[0]
                path = ''.join(path).split('_')[0]  + '/' + i + '.json'
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
    return file.split('/')[2][:-len(ext)-1]

##### IMAGEMAGICK #####
def drw_text_image(text, file):
    with Image(width=1000, height=1000, background=Color('black')) as img:
        img.format = 'png'
        with Drawing() as context:
            tmp = text.getvalue()
            metrics = context.get_font_metrics(img, tmp, True)
            # print(metrics)
            x = 10
            y = 14
            w = int(metrics.text_width*1.2)
            h = int(metrics.text_height*1.3)
            img.resize(w, h)
            # print(img.size)
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
def cat(path, stdout=True):
    try:
        with open(path, 'r') as file:
            content = file.readlines()
            if stdout:
                count = 0
                result = ''
                for l in content:
                    result += l.lstrip()
                    count += 1
                    # print(count + 1, ': ', l, sep='', end='')
                return result
            else: 
                result = io.StringIO()
                for l in content:
                    result.write(l)
                return result
    except Exception as err:
        raise RuntimeError('Cannot open file to read') from err
        return -1

# return the matched line along with next `n` lines
# not so optimized but usable
def cursed_grep(path, regex, number=0):
    result = io.StringIO()
    # call grep() then get line number returned
    line_number = int(grep(path, regex, True, True).split()[0][:-1])
    with open(path, 'r') as f:
        lines = f.readlines()[line_number-1:]
        for i in range(number):
            result.write(lines[i])
    return result

# TODO: remake using StringIO
def grep(path, regex, single_line=True, print_line=False):
    result = ''
    flag = re.MULTILINE
    pattern = re.compile(regex, flag)
    file = cat(path, False)
    content = file.getvalue().split('\n')

    if single_line:
        for line in range(len(content)):
            if re.search(pattern, content[line]):
                result += content[line].lstrip()
                if print_line:
                    result = str(line + 1) + ': ' + result
                # print(result)
                break 
    else:
        for line in range(len(content)):
            if re.search(pattern, content[line]):
                result += content[line].lstrip()
                if print_line:
                    result = str(line + 1) + ': ' + result
                # print(result)
                break
    print()
    return result
##### END BASE #####
