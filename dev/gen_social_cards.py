"""Generate 1200x630 Open Graph / Twitter social cards for each Fabric Arcade game."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "..", "website", "images", "social")
os.makedirs(OUT, exist_ok=True)

FB = r"C:\Windows\Fonts\arialbd.ttf"
FR = r"C:\Windows\Fonts\arial.ttf"
FE = r"C:\Windows\Fonts\seguiemj.ttf"

W, H = 1200, 630

# slug (matches html basename), title, emoji, hashtags, accent RGB
GAMES = [
    ("fabric-racing-game", "Fabric Racing Game", "\U0001F3CE\uFE0F", "#Eventstream", (0, 230, 118)),
    ("calc-groups-cathedral", "Calc Groups Cathedral", "\U0001F3DB\uFE0F", "#CalculationGroups", (255, 209, 102)),
    ("city-builder", "City Builder", "\U0001F3D9\uFE0F", "#Warehouse", (34, 211, 238)),
    ("monster-breach", "Monster Breach", "\U0001F47E", "#DataPipeline", (255, 107, 107)),
    ("ontology-detective", "Ontology Detective", "\U0001F575\uFE0F", "#Ontology  \u00B7  #KQL", (96, 165, 250)),
    ("retro-arcade", "Retro Arcade", "\U0001F579\uFE0F", "#PowerBI", (244, 114, 182)),
]


def lerp(a, b, t):
    return int(a + (b - a) * t)


def gradient(accent):
    top = (13, 13, 26)
    bot = (26, 20, 46)
    img = Image.new("RGB", (W, H), top)
    px = img.load()
    for y in range(H):
        t = y / H
        r = lerp(top[0], bot[0], t)
        g = lerp(top[1], bot[1], t)
        b = lerp(top[2], bot[2], t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return img


def fit_font(path, text, max_w, start, min_size=40):
    size = start
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if f.getbbox(text)[2] <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(path, min_size)


def draw_emoji(img, emoji, cx, cy, size):
    layer = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    try:
        ef = ImageFont.truetype(FE, size)
        d.text((size, size), emoji, font=ef, embedded_color=True, anchor="mm")
    except Exception:
        pass
    img.paste(layer, (cx - size, cy - size), layer)


for slug, title, emoji, tags, accent in GAMES:
    img = gradient(accent)
    d = ImageDraw.Draw(img)

    # accent border
    d.rectangle([8, 8, W - 9, H - 9], outline=accent, width=4)
    d.rectangle([0, 0, W - 1, 6], fill=accent)

    # top-left wordmark
    draw_emoji(img, "\U0001F3AE", 60, 70, 40)
    wf = ImageFont.truetype(FB, 34)
    d.text((92, 70), "FABRIC ARCADE", font=wf, fill=(230, 230, 245), anchor="lm")

    # center emoji
    draw_emoji(img, emoji, W // 2, 250, 150)

    # title
    tf = fit_font(FB, title, W - 160, 92)
    d.text((W // 2, 415), title, font=tf, fill=accent, anchor="mm")

    # subtitle
    sf = ImageFont.truetype(FR, 34)
    d.text((W // 2, 480), "Learn Microsoft Fabric by playing", font=sf, fill=(200, 200, 215), anchor="mm")

    # hashtag chip
    cf = ImageFont.truetype(FB, 30)
    bb = cf.getbbox(tags)
    tw = bb[2] - bb[0]
    pad = 26
    chip_w = tw + pad * 2
    cx0 = (W - chip_w) // 2
    cy0 = 535
    d.rounded_rectangle([cx0, cy0, cx0 + chip_w, cy0 + 56], radius=28, fill=(255, 255, 255, 20), outline=accent, width=2)
    d.text((W // 2, cy0 + 28), tags, font=cf, fill=(235, 235, 245), anchor="mm")

    out = os.path.join(OUT, slug + ".png")
    img.save(out, "PNG")
    print("wrote", os.path.relpath(out))

print("done")
