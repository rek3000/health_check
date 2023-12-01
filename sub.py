#!/usr/bin/env python3

import json, io
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont

from rekdoc.const import *
from rekdoc import tools

import uuid
# def drw_text_image(text, file):
#     with Image(width=1000, height=1000, background=Color("black")) as img:
#         img.format = "png"
#         with Drawing() as context:
#             tmp = text.getvalue()
#             metrics = context.get_font_metrics(img, tmp, True)
#             x = 10
#             y = 14
#             w = int(metrics.text_width * 1.2)
#             h = int(metrics.text_height * 1.3)
#             img.resize(w, h)
#             # context.font_family = "monospace"
#             context.font_size = y
#             context.fill_color = Color("white")
#             context.gravity = "north_west"
#             context.text_antialias = True
#             context.text(x, y, text.getvalue())
#             context(img)
#         img.save(filename="PNG24:" + file)


def drw_text_image(text, file):
    size = 14
    with Image.new("RGB", (1000, 1000)) as img:
        d1 = ImageDraw.Draw(img)
        left, top, right, bottom = d1.textbbox((10, 10), text, font_size=size)
        print(right)
        print(bottom)
        w = int(right * 1.1) + 10
        h = int(bottom * 1.1) + 10
        print(w)
        print(h)
        # img_resize = img.crop((0, 0, w, h))
        img_resize = img.resize((w, h), resample=Image.NEAREST)
        d2 = ImageDraw.Draw(img_resize)
        d2.text((10, 10), text, font_size=size)
        img_resize.save(file + ".png", format="PNG")


if __name__ == "__main__":
    text = "This is a test text\nand this is the second line"
    print(str(uuid.uuid4()).split("-")[-1])

    # text = tools.cat('temp/explorer.86d102c0.DBMC01.market_clearing.com-2023.08.25.03.30' + PARTITION_SOL)
    drw_text_image(text, "hello")
