from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out = Path(__file__).resolve().parent
paper = "#f5f1e8"
ink = "#292823"
wine = "#8b303f"
line = "#d9d2c6"
green = "#386c54"
font_dir = Path(r"C:\Windows\Fonts")
serif = str(font_dir / "georgia.ttf")
serif_bold = str(font_dir / "georgiab.ttf")
mono = str(font_dir / "cour.ttf")

def font(path, size):
    return ImageFont.truetype(path, size)

img = Image.new("RGB", (164, 314), paper)
d = ImageDraw.Draw(img)
d.line((18, 16, 146, 16), fill=line, width=1)
d.ellipse((53, 35, 111, 93), outline=wine, width=2)
d.text((82, 57), "BPD", fill=wine, anchor="mm", font=font(serif, 16))
d.text((82, 119), "Blood,", fill=ink, anchor="mm", font=font(serif_bold, 21))
d.text((82, 145), "in focus.", fill=wine, anchor="mm", font=font(serif, 21))
d.text((82, 180), "BPD", fill=ink, anchor="mm", font=font(mono, 8))
d.text((82, 193), "LOCAL INFERENCE", fill=green, anchor="mm", font=font(mono, 7))
d.line((18, 230, 146, 230), fill=line, width=1)
d.ellipse((28, 252, 34, 258), fill=green)
d.text((42, 249), "MODEL READY", fill=ink, font=font(mono, 7))
img.save(out / "wizard.bmp")

small = Image.new("RGB", (55, 55), paper)
d = ImageDraw.Draw(small)
d.ellipse((7, 7, 48, 48), outline=wine, width=2)
d.text((27, 27), "BPD", fill=wine, anchor="mm", font=font(serif, 12))
small.save(out / "wizard_small.bmp")

icon = Image.new("RGBA", (256, 256), (245, 241, 232, 255))
d = ImageDraw.Draw(icon)
d.ellipse((28, 28, 228, 228), outline=wine, width=9, fill=(252, 250, 245, 255))
d.text((128, 128), "BPD", fill=wine, anchor="mm", font=font(serif_bold, 54))
icon.save(out / "bpd.ico", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
