#!/usr/bin/env python
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import tools

def run():
    text = 'Hello'
    tools.drw_text_image(text, 'hello.png')

def main():
    run()

if __name__ == "__main__":
    main()
