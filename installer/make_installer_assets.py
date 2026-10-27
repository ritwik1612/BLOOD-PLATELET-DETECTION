from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out = Path(__file__).resolve().parent
paper = "#000000"
ink = "#f1e8eb"
wine = "#b53652"
line = "#40232e"
green = "#ae6d7e"
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
d.text((82, 119), "Blood cell", fill=ink, anchor="mm", font=font(serif_bold, 21))
d.text((82, 145), "analysis", fill=wine, anchor="mm", font=font(serif, 21))
d.text((82, 180), "BPD", fill=ink, anchor="mm", font=font(mono, 8))
d.text((82, 193), "LOCAL INFERENCE", fill=green, anchor="mm", font=font(mono, 7))
d.line((18, 230, 146, 230), fill=line, width=1)
d.ellipse((28, 252, 34, 258), fill=green)
d.text((42, 249), "OFFLINE APP", fill=ink, font=font(mono, 7))
img.save(out / "wizard.bmp")

small = Image.new("RGB", (55, 55), paper)
d = ImageDraw.Draw(small)
d.ellipse((7, 7, 48, 48), outline=wine, width=2)
d.text((27, 27), "BPD", fill=wine, anchor="mm", font=font(serif, 12))
small.save(out / "wizard_small.bmp")

# A red-cell icon matching the app's blood-cell illustration, with an alpha edge.
import math
icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
pixels = icon.load()
stops = [(0.0,(28,2,12)),(.32,(49,4,22)),(.56,(107,18,44)),(.72,(182,43,73)),(.83,(216,73,99)),(.92,(145,28,54)),(1.0,(67,7,28))]
angle = math.radians(-22)
for y in range(256):
    for x in range(256):
        dx,dy=x-128,y-128
        u=dx*math.cos(angle)+dy*math.sin(angle)
        v=-dx*math.sin(angle)+dy*math.cos(angle)
        radius=math.sqrt((u/113)**2+(v/82)**2)
        if radius > 1.025:
            continue
        r=min(radius,1.0)
        for (r0,c0),(r1,c1) in zip(stops,stops[1:]):
            if r0<=r<=r1:
                t=(r-r0)/(r1-r0)
                highlight=max(.64,min(1.22,1.0-.15*u/113-.20*v/82))
                color=tuple(max(0,min(255,round((a*(1-t)+b*t)*highlight))) for a,b in zip(c0,c1))
                alpha=round(255*min(1,max(0,(1.025-radius)/.025)))
                pixels[x,y]=(*color,alpha)
                break
icon.save(out / "blood-cell.png")
icon.save(out / "bpd.ico", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
