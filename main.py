def grep(path, word):
    with open(path, 'r') as file:
        content = file.readlines()

        count = 0
        for line in range(0, len(content)):
            if content[line].find(word) != -1:
                print(line + 1, ': ', content[line], sep='', end='')
            
def print_file(path):
    with open(path, 'r') as file:
        content = file.readlines()
        count = 0
        for line in range(0, len(content)):
            print(line + 1, ': ', content[line], sep='', end='')
def save_file(file, content):
    with open(file, 'w') as file:
        file.write(content)

def main():

    path=input('Enter path to log folder(ILOM): ')
    print_file(path + '/fma/@usr@local@bin@fmadm_faulty.out')
    print()
    grep(path + '/ilom/@usr@local@bin@collect_properties.out', '_temp')
    print()
    grep(path + '/ilom/@usr@local@bin@spshexec_version.out', 'SP firmware')


if __name__ == "__main__":
    main()
