"""Generate demo assets: a stylized demo portrait + garment reference images.

All assets are original, generated locally with PIL — no external images,
no copyright issues.
"""

import os

from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, "static", "assets")
os.makedirs(ASSETS, exist_ok=True)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def demo_portrait():
    """Stylized flat-illustration portrait for demo mode (head + shoulders)."""
    img = Image.new("RGB", (480, 640), "#f3ede4")
    d = ImageDraw.Draw(img)
    skin = hex_to_rgb("#b9947c")
    hair = hex_to_rgb("#2e1d14")
    # shoulders / top
    d.ellipse([120, 430, 360, 640], fill="#3a4a63")
    # neck
    d.rectangle([210, 330, 270, 460], fill=skin)
    # face
    d.ellipse([170, 150, 310, 350], fill=skin)
    # hair
    d.ellipse([160, 110, 320, 260], fill=hair)
    d.rectangle([160, 200, 320, 260], fill=hair)
    d.ellipse([170, 150, 310, 300], fill=skin)  # face over hair
    # eyes
    d.ellipse([200, 235, 230, 250], fill="#ffffff")
    d.ellipse([250, 235, 280, 250], fill="#ffffff")
    d.ellipse([209, 238, 221, 248], fill="#2b1d16")
    d.ellipse([259, 238, 271, 248], fill="#2b1d16")
    # brows + lips
    d.rectangle([198, 220, 232, 226], fill=hair)
    d.rectangle([248, 220, 282, 226], fill=hair)
    d.ellipse([225, 300, 258, 314], fill="#a05a58")
    # blush
    d.ellipse([185, 270, 210, 285], fill="#c98f7a")
    d.ellipse([270, 270, 295, 285], fill="#c98f7a")
    img.save(os.path.join(ASSETS, "demo_portrait.png"))


def garment(gid, color, label, shape="blouse"):
    """Flat garment reference in its color, with the garment name."""
    img = Image.new("RGB", (400, 400), "#f7f5f2")
    d = ImageDraw.Draw(img)
    c = hex_to_rgb(color)
    if shape == "dress":
        d.polygon([(200, 40), (120, 120), (150, 120), (100, 380),
                   (300, 380), (250, 120), (280, 120)], fill=c)
    elif shape == "coat":
        d.polygon([(200, 40), (110, 110), (140, 110), (120, 380),
                   (280, 380), (260, 110), (290, 110)], fill=c)
        d.rectangle([196, 40, 204, 380], fill=(0, 0, 0, 40))
    elif shape == "scarf":
        d.polygon([(60, 160), (340, 120), (330, 200), (70, 240)], fill=c)
        d.polygon([(60, 250), (330, 210), (320, 290), (70, 330)], fill=c)
    else:  # blouse
        d.polygon([(200, 40), (110, 90), (140, 90), (130, 300),
                   (270, 300), (260, 90), (290, 90)], fill=c)
    d.rectangle([0, 360, 400, 400], fill=(20, 20, 24))
    d.text((12, 372), label, fill=(255, 255, 255))
    img.save(os.path.join(ASSETS, f"garment_{gid}.png"))


GARMENTS = [
    ("g1", "#C1553B", "Terracotta Silk Blouse", "blouse"),
    ("g2", "#1F2A44", "Midnight Navy Blazer", "coat"),
    ("g3", "#0E7C5B", "Emerald Satin Dress", "dress"),
    ("g4", "#D9A441", "Mustard Knit Sweater", "blouse"),
    ("g5", "#B81E3A", "Crimson Paisley Scarf", "scarf"),
    ("g6", "#3A3A3E", "Charcoal Wool Coat", "coat"),
    ("g7", "#EFE6D5", "Ivory Linen Shirt", "blouse"),
    ("g8", "#2B3A9B", "Royal Indigo Kurta", "blouse"),
]

if __name__ == "__main__":
    demo_portrait()
    for gid, color, label, shape in GARMENTS:
        garment(gid, color, label, shape)
    print("assets written to", ASSETS)
