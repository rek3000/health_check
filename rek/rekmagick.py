#!/usr/bin/env python
import tools
import io
import re

def run():
    path = './temp/DBMC01_ILOM_AK00411154_2023-08-25T11-09-15/ilom/@usr@local@bin@collect_properties.out'
    cooling = io.StringIO()
    cooling.write(path + '\n')
    reg = '^ /System/Cooling$'
    cooling. write(tools.cursed_grep(path, reg, 8).getvalue())
    print(cooling.getvalue())
    tools.drw_text_image(cooling, 'df.png')


def main():
    run()

if __name__ == "__main__":
    main()
