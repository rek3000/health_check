import json
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

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
                path = './output/' + i + '.json'
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
    with Image(width=1024, height=600, background=Color('black')) as img:
        img.format = 'png'
        x = int((img.width - len(text.split('\n')[0])*20)/3)
        print(x)
        y = 12
        with Drawing() as context:
            context.font_family = 'monospace'
            context.font_size = y
            context.fill_color = Color('white')
            metrics = context.get_font_metrics(
                    img,
                    text,
                    multiline=True
                    )

            # context.text(int(img.width // 4), int(img.height // 4), text)
            a = text.split('\n')[0]
            print(a)
            print(len(a))
            info = context.text(x, y, text)
            context(img)
            # print(metrics)
            img.save(filename='PNG24:' + file)
##### END OF IMAGEMAGICK #####
