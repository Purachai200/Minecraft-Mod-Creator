"""CurseForge art: logo (400x400), header banner (1920x480) and the arsenal lineup poster (1920x1080).

  python3 tools/build_showcase.py      (run from the "Youjo Senki Arms" folder; writes showcase/)

Guns are rendered from the generated geo/texture files with the same renderer as the inventory icons,
so run tools/build_gun_assets.py first.
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from build_gun_assets import icon

A = "src/main/resources/tacz_youjoarms/assets/youjoarms"
CIRCLE = "src/main/resources/assets/youjoarms/textures/vfx/magic_circle.png"
SEAL = "src/main/resources/assets/youjoarms/textures/vfx/circle_seal.png"
OUT = "showcase"
TITLE = "/System/Library/Fonts/Supplemental/Copperplate.ttc"
BODY = "/System/Library/Fonts/Avenir Next.ttc"
GOLD, CYAN = (232, 196, 110), (110, 235, 255)
GUNS = [("kar98k", "Karabiner 98k"), ("gewehr98", "Gewehr 98"), ("t_gewehr", "T-Gewehr 1918"), ("mosin", "Mosin-Nagant"),
        ("lebel", "Lebel 1886"), ("lee_enfield", "SMLE Mk III"), ("mg08_15", "MG 08/15"), ("mg08", "MG 08"),
        ("mp18", "MP 18"), ("m1897", "M1897 Trench Gun"), ("c96", "Mauser C96"), ("luger_p08", "Luger P08"),
        ("kampfpistole", "Kampfpistole")]


def gun_art(gun, w, h):
    geo = json.load(open(f"{A}/geo_models/gun/{gun}_geo.json"))
    tex = Image.open(f"{A}/textures/gun/uv/{gun}.png").convert("RGBA")
    return icon(geo, tex, w, h, yaw=-90, outline=False)  # right side, muzzle pointing right


def backdrop(w, h):
    """Night-blue gradient with a faint tinted magic circle glow."""
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = y / h
            d = math.hypot(x / w - 0.5, y / h - 0.45)
            px[x, y] = (int(14 + 18 * (1 - t) - 10 * d), int(18 + 22 * (1 - t) - 10 * d), int(34 + 30 * (1 - t) - 12 * d), 255)
    return img


def tinted(path, size, color, alpha=1.0):
    c = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    # fade to zero before the square edge: the glow halo otherwise leaves a faint box on dark backgrounds
    fade = Image.new("L", c.size, 0)
    ImageDraw.Draw(fade).ellipse([size * 0.02, size * 0.02, size * 0.98, size * 0.98], fill=255)
    fade = fade.filter(ImageFilter.GaussianBlur(size * 0.02))
    a = Image.composite(c.split()[3], Image.new("L", c.size, 0), fade)
    layer = Image.new("RGBA", c.size, color + (0,))
    layer.putalpha(a.point(lambda v: int(v * alpha)))
    return layer


def glow_text(img, xy, text, font, fill, glow=(0, 0, 0), anchor="mm", blur=6):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(xy, text, font=font, fill=glow + (255,), anchor=anchor)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(img).text(xy, text, font=font, fill=fill, anchor=anchor)


def logo():
    img = backdrop(400, 400)
    img.alpha_composite(tinted(CIRCLE, 380, CYAN, 0.9), (10, 10))
    img.alpha_composite(tinted(SEAL, 210, GOLD, 0.55), (95, 95))
    gun = gun_art("kar98k", 420, 140).rotate(28, expand=True, resample=Image.BICUBIC)
    shadow = Image.new("RGBA", gun.size, (0, 0, 0, 0))
    shadow.putalpha(gun.split()[3].filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(shadow, ((400 - gun.width) // 2 + 4, (400 - gun.height) // 2 + 8))
    img.alpha_composite(gun, ((400 - gun.width) // 2, (400 - gun.height) // 2))
    glow_text(img, (200, 352), "ARCANE INFANTRY", ImageFont.truetype(TITLE, 34), GOLD)
    return img.convert("RGB")


def banner():
    w, h = 1920, 480
    img = backdrop(w, h)
    img.alpha_composite(tinted(CIRCLE, 760, CYAN, 0.55), (w - 820, -140))
    img.alpha_composite(tinted(SEAL, 420, GOLD, 0.35), (w - 640, 30))
    gun = gun_art("kar98k", 820, 300)
    img.alpha_composite(gun, (w - 860, 360 - gun.height))
    glow_text(img, (90, 170), "ARCANE INFANTRY", ImageFont.truetype(TITLE, 92), GOLD, anchor="lm")
    glow_text(img, (94, 262), "Mage-infantry rifles & battle formulas for TACZ", ImageFont.truetype(BODY, 40), (220, 230, 240), anchor="lm")
    glow_text(img, (94, 330), "13 WWI-era firearms  ·  7 stacked-circle formulas  ·  works with any TACZ attachment pack",
              ImageFont.truetype(BODY, 28), CYAN, anchor="lm", blur=4)
    return img.convert("RGB")


def lineup():
    w, h = 1920, 1080
    img = backdrop(w, h)
    img.alpha_composite(tinted(CIRCLE, 1000, CYAN, 0.18), (460, 60))
    glow_text(img, (w // 2, 70), "THE ARSENAL", ImageFont.truetype(TITLE, 64), GOLD)
    name_font = ImageFont.truetype(BODY, 26)
    rows = (len(GUNS) + 1) // 2
    cell_w, cell_h = 900, (h - 150) // rows
    for k, (gun, name) in enumerate(GUNS):
        col, row = k // rows, k % rows
        x0, y0 = 60 + col * (cell_w + 60), 130 + row * cell_h
        art = gun_art(gun, cell_w - 320, cell_h - 10)
        img.alpha_composite(art, (x0 + 310, y0 + (cell_h - art.height) // 2))
        ImageDraw.Draw(img).text((x0, y0 + cell_h // 2), name, font=name_font, fill=(230, 232, 236), anchor="lm")
    return img.convert("RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    logo().save(f"{OUT}/logo.png")
    banner().save(f"{OUT}/banner.png")
    lineup().save(f"{OUT}/arsenal.png")
    print("wrote", OUT)
