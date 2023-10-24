import json

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
        with open(file, 'r+') as f:
            content = json.load(f)
        return content
    except OSError as err:
        print('OS error: ', err)
        raise RuntimeError('Cannot read JSON') from err
        return -1

def join_json(output):
    try:
        with open('./output/data.json', 'a+') as file:
            x = {}
            for i in output:
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
