from PIL import Image, ImageDraw, ImageFont
import io

def drw_text_image(text, file):
    size = 16
    font_path = "monospace"  # Adjust the font path if needed
    try:
        font = ImageFont.truetype(font_path, size=size)
    except OSError:
        font = ImageFont.load_default(size)
    except Exception:
        font = ImageFont.load_default()

    # Replace tabs with spaces

    with Image.new("RGB", (800, 600)) as img:
        draw = ImageDraw.Draw(img)
        draw.fontmode = "RGB"

        x = 10
        y = 10
        line_height = font.getbbox('A')[3]
        char_spacing = 1.5  # Adjust this value based on your preference

        for line in text.split("\n"):
            columns = line.split()
            column_widths = [font.getbbox(col)[2] for col in columns]

            for col, width in zip(columns, column_widths):
                draw.text((x, y), col, font=font)
                x += int(width * char_spacing)

            x = 10  # Reset X for the next line
            y += line_height

        img.save(file, format="PNG")

# Example usage:
sample_text = r"""NAME              CLASS/TYPE STATE        UNDER      ADDR
aggr523000        ip         ok           --         --
   aggr523000/v4  static     ok           --         10.0.132.210/22
lo0               loopback   ok           --         --
   lo0/v4         static     ok           --         127.0.0.1/8
   lo0/v6         static     ok           --         ::1/128
sp-host0          ip         ok           --         --
   sp-host0/v4    static     ok           --         169.254.182.77/24
vnic0             ip         ok           --         --
   vnic0/v4       static     ok           --         10.0.0.2/24"""

sample_text = sample_text.replace('\t', '    ')

with io.StringIO(sample_text) as text_buffer:
    print(sample_text)
    drw_text_image(text_buffer.getvalue(), 'output_image.png')
