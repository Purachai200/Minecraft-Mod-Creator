"""Builds the youjoarms gun models, textures and inventory/HUD icons for the TACZ gun pack.

  python3 tools/build_gun_assets.py            (run from the "Youjo Senki Arms" folder)

Each gun keeps the bone tree of a TACZ built-in gun with the same action (m700 = bolt action, m1911 = pistol,
hk_mp5a5 = SMG) so the built-in animations ("tacz:m700" etc.) drive our model. All donor cubes are dropped and
replaced with our own; only bone names/pivots are kept (plus a few pivot overrides for barrel length and sights).
Geo space: front of the gun is -Z, its right side is -X, 1 unit = 1/16 block.
"""
import json, math, os, re, sys, zipfile
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import preview_geo

JAR = "libs/tacz-1.20.1-1.1.6-hotfix.jar"
DONOR = "assets/tacz/custom/tacz_default_gun/assets/tacz/geo_models/gun/{}_geo.json"
PACK = "src/main/resources/tacz_youjoarms/assets/youjoarms"
P = 12  # texels per model unit

# ---------------------------------------------------------------- primitives

def box(x0, x1, y0, y1, z0, z1, m, rot=None, piv=None, decal=None):
    c = {"o": [min(x0, x1), min(y0, y1), min(z0, z1)], "s": [abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)], "m": m}
    if rot:
        c["rot"], c["piv"] = rot, piv
    if decal:
        c["decal"] = decal
    return c


def _strips(r):
    """Strips needed for a regular 2n-gon: 1 = plain square bar, else 4 -> 8-gon, 6 -> 12-gon, 8 -> 16-gon."""
    return 1 if r < 0.22 else 4 if r < 0.5 else 6 if r < 1.1 else 8


def rod(y, r, z0, z1, m, x=0.0, decal=None):
    """Round bar along Z. A regular 2n-gon is the union of n flat strips turned 180/n degrees apart (a union of
    squares would be a spiky star). Each strip's long inside faces are hidden, so they cost no texture."""
    n = _strips(r)
    if n == 1:
        a = r * 0.9
        return [box(x - a, x + a, y - a, y + a, z0, z1, m, decal=decal)]
    a = r * math.cos(math.pi / (2 * n))
    t = 2 * a * math.tan(math.pi / (2 * n))
    out = []
    for k in range(n):
        c = box(x - a, x + a, y - t / 2, y + t / 2, z0, z1, m,
                rot=[0, 0, k * 180.0 / n] if k else None, piv=[x, y, (z0 + z1) / 2])
        c["hide"] = ("up", "down")
        out.append(c)
    return out


def yrod(x, z, r, y0, y1, m):
    """Round post along Y (same regular-polygon construction, strips turned about Y)."""
    n = max(4, _strips(r))
    a = r * math.cos(math.pi / (2 * n))
    t = 2 * a * math.tan(math.pi / (2 * n))
    out = []
    for k in range(n):
        c = box(x - a, x + a, y0, y1, z - t / 2, z + t / 2, m, rot=[0, k * 180.0 / n, 0] if k else None, piv=[x, 0, z])
        c["hide"] = ("north", "south")
        out.append(c)
    return out


def slab(z0, y0, z1, y1, t, w, m, top=True, x=0.0, trim=False):
    """Box of thickness t whose top (or bottom) face runs along the line (z0,y0)->(z1,y1).
    trim shortens it so its inner corner does not poke out past z1 (last segment of a stock)."""
    L, ang = math.hypot(z1 - z0, y1 - y0), math.degrees(math.atan2(y1 - y0, z1 - z0))
    if trim:
        L -= t * abs(math.sin(math.radians(ang)))
    ya, yb = (y0 - t, y0) if top else (y0, y0 + t)
    return box(x - w / 2, x + w / 2, ya, yb, z0, z0 + L, m, rot=[ang, 0, 0], piv=[x, y0, z0])


def smooth(pts, step=1.4):
    """Subdivide a stock outline (z, top, bottom, width) with Hermite curves so combs, wrists and butts flow instead
    of being straight wedges. Values are clamped to their segment's range, so flat runs stay flat."""
    if len(pts) < 3 or pts[-1][0] - pts[0][0] < 6:
        return pts
    out = [tuple(pts[0])]
    last = len(pts) - 1
    for k in range(last):
        p0, p1, p2, p3 = pts[max(0, k - 1)], pts[k], pts[k + 1], pts[min(last, k + 2)]
        L = p2[0] - p1[0]
        n = max(1, round(L / step))
        for q in range(1, n + 1):
            t = q / n
            h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
            row = [p1[0] + L * t]
            for c in (1, 2, 3):
                m1 = (p2[c] - p0[c]) / max(1e-6, p2[0] - p0[0]) * L
                m2 = (p3[c] - p1[c]) / max(1e-6, p3[0] - p1[0]) * L
                v = h00 * p1[c] + h10 * m1 + h01 * p2[c] + h11 * m2
                lo, hi = min(p1[c], p2[c]), max(p1[c], p2[c])
                pad = 0.12 * (hi - lo) + 0.01
                row.append(max(lo - pad, min(hi + pad, v)))
            out.append(tuple(row))
    return out


def profile(pts, m, x=0.0, bevel=0.14):
    """Wooden stock from control points (z, top, bottom, width). Each segment is a full-width body inset by
    {bevel} top and bottom plus a narrower full-height body, so the cross-section has chamfered (rounded-looking)
    edges; sloped runs get the same two-part skins."""
    out = []
    pts = smooth(pts)
    last = len(pts) - 2
    e = bevel
    for k, ((z0, t0, b0, w0), (z1, t1, b1, w1)) in enumerate(zip(pts, pts[1:])):
        w = (w0 + w1) / 2
        trim = k == last
        for width, inset in ((w, e), (w - 2 * e, 0.0)):
            core_t, core_b = min(t0, t1) - inset, max(b0, b1) + inset
            if core_t > core_b:
                out.append(box(x - width / 2, x + width / 2, core_b, core_t, z0, z1, m))
            if abs(t1 - t0) > 0.05:
                out.append(slab(z0, t0 - inset, z1, t1 - inset, abs(t1 - t0) + 0.35, width, m, top=True, x=x, trim=trim))
            if abs(b1 - b0) > 0.05:
                out.append(slab(z0, b0 + inset, z1, b1 + inset, abs(b1 - b0) + 0.35, width, m, top=False, x=x, trim=trim))
    return out


def sling(points, x, m="leather", w=0.42, t=0.07):
    """Flat strap through (z, y) points on the gun's left side (+x)."""
    return [slab(z0, y0, z1, y1, w, t, m, top=True, x=x) for (z0, y0), (z1, y1) in zip(points, points[1:])]


def cartridge(lo, hi, tip=True, scale=1.0):
    """A round filling the donor bullet bounds. Long axis = largest extent; the tip sits at max Y (donor convention)."""
    ext = [hi[i] - lo[i] for i in range(3)]
    ax = ext.index(max(ext))
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    r = min(e for i, e in enumerate(ext) if i != ax) / 2 * scale
    a0, a1 = lo[ax], hi[ax]
    n = a1 - a0
    parts = []

    def seg(s0, s1, rr, m):
        q0, q1 = [c[i] - rr for i in range(3)], [c[i] + rr for i in range(3)]
        q0[ax], q1[ax] = s0, s1
        parts.append(box(q0[0], q1[0], q0[1], q1[1], q0[2], q1[2], m))

    if ax == 2:  # lying along Z: tip toward -Z
        seg(a0 + n * 0.62 if tip else a0, a1, r, "brass")
        if tip:
            seg(a0 + n * 0.25, a0 + n * 0.62, r * 0.7, "brass")
            seg(a0, a0 + n * 0.25, r * 0.5, "copper")
    else:
        seg(a0, a1 - n * 0.38 if tip else a1, r, "brass")
        if tip:
            seg(a1 - n * 0.38, a1 - n * 0.25, r * 0.7, "brass")
            seg(a1 - n * 0.25, a1, r * 0.5, "copper")
    return parts

def shotshell(lo, hi):
    """12-gauge shell in the donor bullet bounds: brass head, red paper hull, crimped top at max Y."""
    ext = [hi[i] - lo[i] for i in range(3)]
    ax = ext.index(max(ext))
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    r = min(e for i, e in enumerate(ext) if i != ax) / 2
    a0, a1 = lo[ax], hi[ax]
    head = a0 + (a1 - a0) * 0.3 if ax != 2 else a1 - (a1 - a0) * 0.3
    out = []
    for s0, s1, m, rr in ((a0, head, "brass", r), (head, a1, "red", r * 0.92)) if ax != 2 else ((head, a1, "brass", r), (a0, head, "red", r * 0.92)):
        q0, q1 = [c[i] - rr for i in range(3)], [c[i] + rr for i in range(3)]
        q0[ax], q1[ax] = s0, s1
        out.append(box(q0[0], q1[0], q0[1], q1[1], q0[2], q1[2], m))
    return out


# ---------------------------------------------------------------- guns

def bolt_rifle_extras(B, z0=0.0, z1=6.6, bolt_z=8.2, floor_z=(8.4, 11.6)):
    """Metalwork every bolt rifle shares: raised receiver rings, bolt-stop lever, trigger-guard bow with screws,
    magazine floor plate and release, rear tang screw, cocking-piece slot."""
    out = rod(B, 0.80, z0 + 0.1, z0 + 0.45, "steel") + rod(B, 0.80, z1 - 0.45, z1 - 0.1, "steel")   # receiver rings
    out.append(box(0.70, 0.98, B - 0.5, B - 0.05, z0 + 2.0, z0 + 3.9, "steel"))                      # bolt-stop lever
    out.append(box(0.72, 0.78, B - 0.6, B - 0.1, z0 + 2.2, z0 + 3.0, "dark"))
    out.append(box(-0.30, 0.30, 3.62, 3.78, floor_z[0], floor_z[1], "steel", decal="panel"))        # floor plate
    out.append(box(-0.16, 0.16, 3.55, 3.85, floor_z[0] - 0.3, floor_z[0] + 0.3, "bright"))           # release button
    for sx in (-1, 1):                                                                              # guard screws
        out.append(box(sx * 0.46, sx * 0.50, 4.7, 5.2, 1.8, 2.4, "steel", decal="screw"))
        out.append(box(sx * 0.46, sx * 0.50, 4.7, 5.2, floor_z[1] - 1.0, floor_z[1] - 0.4, "steel", decal="screw"))
    out.append(box(-0.2, 0.2, B + 0.3, B + 0.52, bolt_z + 1.4, bolt_z + 2.4, "steel"))               # tang
    return out


def mauser_rifle(muzzle, gew=False, bent=None):
    """Kar98k (gew=False) or Gewehr 98 on the m700 rig. Bore y=7.25, sight line y=8.406 (m700 iron_view)."""
    B, S = 7.25, 8.406
    nose = muzzle + (7.5 if not gew else 9.5)
    body = []
    # barrel (stepped) and muzzle crown
    body += rod(B, 0.30, muzzle, nose, "steel")
    body += rod(B, 0.36, nose, -6, "steel")
    body += rod(B, 0.42, -6, 0.2, "steel")
    body += rod(B, 0.16, muzzle - 0.05, muzzle + 0.1, "dark")
    # front sight: base ring, blade, protective hood (Kar98k only)
    body += rod(B, 0.40, muzzle + 0.25, muzzle + 1.25, "steel")
    body.append(box(-0.07, 0.07, B + 0.3, S, muzzle + 0.55, muzzle + 0.85, "steel"))
    if not gew:
        for sx in (-1, 1):
            body.append(box(sx * 0.25, sx * 0.32, B + 0.25, S + 0.24, muzzle + 0.3, muzzle + 1.15, "steel"))
        body.append(box(-0.32, 0.32, S + 0.18, S + 0.25, muzzle + 0.3, muzzle + 1.15, "steel"))
    # nose cap with bayonet lug, upper/lower bands
    body.append(box(-0.68, 0.68, 6.0, B + 0.44, nose - 0.4, nose + 0.9, "steel"))
    body.append(box(-0.22, 0.22, 5.55, 6.05, nose - 1.4, nose + 0.9, "steel"))  # bayonet lug bar
    body += rod(6.35, 0.11, nose - 1.6, nose, "steel")  # cleaning rod tip
    lower_band = -7.5 if not gew else -9.5
    body.append(box(-0.72, 0.72, 5.75, B + 0.62, lower_band - 0.6, lower_band, "steel", decal="screw"))
    body.append(box(0.72, 0.86, 5.95, 6.55, lower_band - 0.55, lower_band - 0.05, "steel"))  # sling swivel
    body.append(box(0.80, 0.88, 5.25, 6.0, lower_band - 0.7, lower_band + 0.1, "dark"))
    # rear sight: Kar98k tangent leaf / Gewehr 98 "Lange" roller-coaster sight
    rs = -2.6
    if not gew:
        body.append(box(-0.42, 0.42, B + 0.35, 7.95, rs - 1.2, rs + 1.6, "steel"))
        body.append(slab(rs - 0.9, 8.15, rs + 1.4, 7.95, 0.2, 0.62, "steel"))
        notch_z = rs - 1.0
    else:
        body.append(box(-0.45, 0.45, B + 0.35, 7.9, rs - 3.2, rs + 1.4, "steel"))
        body.append(slab(rs - 3.0, 8.2, rs + 1.2, 7.9, 0.3, 0.7, "steel"))
        notch_z = rs - 3.0
    for sx in (-1, 1):  # notch ears; the notch bottom is the sight line
        body.append(box(sx * 0.09, sx * 0.36, 8.1, S + 0.18, notch_z - 0.15, notch_z + 0.25, "steel"))
    body.append(box(-0.36, 0.36, 8.1, S, notch_z - 0.15, notch_z + 0.25, "steel"))
    # receiver: front ring, bridge, walls; elenium rune band around the ring
    body += rod(B, 0.74, -0.2, 2.0, "steel")
    body += rod(B, 0.76, 0.6, 1.0, "glow")
    body.append(box(0.42, 0.66, 6.55, 7.85, 2.0, 6.6, "steel", decal="serial"))  # left wall
    body.append(box(-0.66, -0.42, 6.55, 7.25, 2.0, 6.6, "steel"))    # right wall, low for the handle
    body.append(box(-0.66, 0.66, 6.45, 6.75, 2.0, 6.6, "steel"))
    body += rod(B, 0.72, 6.6, 7.8, "steel")
    body.append(box(0.40, 0.70, 7.55, 7.95, 6.6, 7.8, "steel"))      # stripper clip guide
    body.append(box(-0.70, -0.40, 7.55, 7.95, 6.6, 7.8, "steel"))
    # trigger guard and floorplate
    body.append(box(-0.46, 0.46, 4.82, 5.08, 1.2, 8.6, "steel"))
    body.append(box(-0.20, 0.20, 3.82, 5.0, 8.4, 8.75, "steel"))
    body.append(box(-0.20, 0.20, 3.72, 3.95, 8.6, 11.0, "steel"))
    body.append(slab(11.0, 3.84, 12.0, 4.95, 0.22, 0.4, "steel", top=False))
    body.append(box(-0.09, 0.09, 4.0, 5.0, 9.55, 9.85, "steel", rot=[-14, 0, 0], piv=[0, 5.0, 9.7]))  # trigger
    # wood: main stock (z,top,bottom,width) then the upper handguard
    fore_top = B - 0.05
    stock = [(nose + 0.9, fore_top, 6.15, 1.18), (lower_band, fore_top, 5.85, 1.30), (0.0, 7.05, 5.2, 1.40),
             (1.2, 7.0, 4.9, 1.50), (8.6, 7.0, 4.9, 1.50), (11.0, 6.95, 5.0, 1.36), (12.3, 6.6, 4.1, 1.26),
             (13.6, 6.3, 3.55, 1.28), (14.6, 6.25, 3.75, 1.30), (15.4, 6.25, 4.05, 1.36), (25.6, 6.75, 1.85, 1.62)]
    if gew:  # Gewehr 98: straighter grip, a touch longer
        stock[-1] = (26.0, 6.8, 1.9, 1.62)
    body += profile(stock, "wood")
    body.append(box(-0.5, 0.5, B + 0.2, 7.82, nose + 1.6 if gew else nose + 3.4, -1.2, "wood"))  # handguard

    # Recoil cross-bolt through stock (recoil lug pin)
    for sx in (-1, 1):
        body.append(box(sx * 0.72, sx * 0.76, 5.6, 6.2, 0.8, 1.4, "steel", decal="screw"))

    # Butt plate: Kar98k has cupped steel plate wrapping around wood edges; Gewehr 98 has flat plate
    if not gew:
        body.append(box(-0.84, 0.84, 1.75, 6.9, 25.6, 26.05, "steel", decal="screw"))  # butt plate rear
        body.append(box(-0.86, 0.86, 1.70, 6.95, 25.0, 25.6, "steel"))                 # cupped rim wrapping forward
    else:
        body.append(box(-0.84, 0.84, 1.80, 6.9, 26.0, 26.45, "steel", decal="screw"))

    # finger grooves along both sides of the fore-end, and a taut leather sling on the left side
    for sx in (-1, 1):
        body.append(box(sx * 0.6, sx * 0.67, 6.45, 6.6, nose + 2.0, lower_band - 1.0, "groove"))
    body += sling([(lower_band - 0.3, 5.75), (6.0, 4.35), (20.8, 3.35)], 0.86)
    body.append(box(-0.84, 0.84, 6.55, 6.9, 23.8, 26.05, "steel"))  # butt plate tang
    body.append(box(-0.84, -0.81, 4.4, 5.75, 17.2, 18.55, "steel"))  # bolt disassembly disc (right side)
    body.append(box(0.81, 0.84, 3.0, 3.6, 19.5, 22.0, "dark"))       # sling slot
    body.append(box(-0.84, -0.81, 3.0, 3.6, 19.5, 22.0, "dark"))
    body.append(box(0.80, 0.83, 4.8, 5.9, 20.0, 21.6, "brass", decal="crest"))  # unit plate

    # bolt (in the m700 "rotate" bone): bright bolt body, shroud, safety flag, handle with pear knob
    bolt = rod(B + 0.05, 0.40, 1.6, 8.8, "bright")
    bolt += rod(B - 0.05, 0.36, 8.8, 10.2, "steel")
    bolt.append(box(-0.06, 0.06, 7.6, 8.25, 9.6, 10.0, "steel"))
    hz0, hz1 = 7.8, 8.4
    if bent if bent is not None else not gew:  # turned-down handle (Kar98k, sniper rifles)
        bolt.append(box(-1.45, -0.3, B - 0.12, B + 0.2, hz0, hz1, "bright"))
        bolt.append(box(-1.85, -1.5, 6.25, B + 0.2, hz0, hz1, "bright", rot=[0, 0, -22], piv=[-1.45, B + 0.1, 8.1]))
        bolt += rod(5.95, 0.40, hz0 - 0.15, hz1 + 0.15, "bright", x=-2.2)
    else:  # Gewehr 98: straight handle
        bolt.append(box(-2.0, -0.3, B - 0.12, B + 0.2, hz0, hz1, "bright"))
        bolt += rod(B + 0.04, 0.40, hz0 - 0.15, hz1 + 0.15, "bright", x=-2.25)
    striker = [box(-0.12, 0.12, 6.45, 6.75, 9.9, 10.9, "steel")]

    body += bolt_rifle_extras(B)
    return {"main_body": body, "rotate": bolt, "striker": striker}


def t_gewehr():
    """Mauser 1918 T-Gewehr on the m700 rig: huge single-shot 13.2 mm with a ported muzzle brake, finned heavy barrel,
    ribbed receiver, folding bipod on a clamp, pistol grip and a padded cheek-rest stock."""
    B, S, muzzle = 7.25, 8.406, -46.0
    body = []
    body += rod(B, 0.46, muzzle + 3.0, -14, "steel")
    body += rod(B, 0.58, -14, 0.0, "steel")
    for z in (-38.0, -31.0, -24.0, -17.5):                                   # barrel collars
        body += rod(B, 0.56, z, z + 0.5, "steel")
    body += rod(B, 0.62, muzzle, muzzle + 3.0, "steel")                      # ported muzzle brake
    body += rod(B, 0.30, muzzle - 0.05, muzzle + 0.1, "dark")
    for k in range(3):
        body.append(box(-0.68, 0.68, B - 0.14, B + 0.14, muzzle + 0.5 + k * 0.8, muzzle + 0.9 + k * 0.8, "dark"))
        body.append(box(-0.14, 0.14, B - 0.68, B + 0.68, muzzle + 0.5 + k * 0.8, muzzle + 0.9 + k * 0.8, "dark"))
    body += rod(B, 0.56, muzzle + 3.0, muzzle + 3.5, "steel")
    body.append(box(-0.5, 0.5, B + 0.4, B + 0.7, muzzle + 3.8, muzzle + 5.2, "steel"))   # front sight foot
    body.append(box(-0.08, 0.08, B + 0.7, S, muzzle + 4.2, muzzle + 4.6, "steel"))
    for sx in (-1, 1):
        body.append(box(sx * 0.32, sx * 0.44, B + 0.7, S + 0.32, muzzle + 4.0, muzzle + 4.8, "steel"))
    # rear sight on the barrel: base, ladder leaf, notch ears
    body.append(box(-0.5, 0.5, B + 0.5, 8.0, -9.5, -6.0, "steel", decal="panel"))
    body.append(slab(-9.2, 8.5, -6.3, 8.0, 0.2, 0.7, "steel"))
    for sx in (-1, 1):
        body.append(box(sx * 0.10, sx * 0.40, 8.0, S + 0.22, -8.4, -8.0, "steel"))
    body.append(box(-0.40, 0.40, 8.0, S, -8.4, -8.0, "steel"))
    # receiver: heavy round body, glow bands (Empire), top rib, ejection port, lock lugs, bolt guide
    body += rod(B, 0.98, -0.6, 7.6, "steel")
    body += rod(B, 1.0, 0.2, 0.6, "glow") + rod(B, 1.0, 6.6, 7.0, "glow")
    body.append(box(-0.5, 0.5, B + 0.9, B + 1.2, -0.4, 7.4, "steel", decal="ribs"))                 # top rib
    body.append(box(0.85, 1.05, B - 0.5, B + 0.5, 1.0, 5.0, "steel", decal="serial"))
    body.append(box(-1.06, -0.9, B - 0.2, B + 0.7, 1.4, 4.4, "dark"))                                 # ejection port
    body.append(box(-1.0, 1.0, 5.9, 6.4, 0.0, 9.0, "steel", decal="panel"))                           # trigger plate
    for sx in (-1, 1):
        body.append(box(sx * 0.9, sx * 1.1, 6.0, 6.5, 6.0, 8.2, "steel", decal="screw"))
    # wood fore-end, steel barrel band and a real folding bipod (clamp, hinge, two legs, feet)
    body += profile([(-16.0, 6.95, 5.6, 1.5), (-1.0, 7.0, 5.0, 1.8), (0.0, 6.6, 5.2, 1.8)], "wood")
    body.append(box(-1.0, 1.0, 5.4, 7.6, -17.0, -15.8, "steel", decal="screw"))
    for sx in (-1, 1):
        body.append(box(sx * 0.35, sx * 0.65, 5.0, 5.3, -16.5, -4.0, "steel"))
        body.append(box(sx * 0.30, sx * 0.70, 4.85, 5.35, -4.6, -3.6, "dark"))
        body.append(box(sx * 0.30, sx * 0.70, 4.55, 5.0, -15.0, -14.4, "steel", decal="screw"))       # hinge
        body.append(box(sx * 0.4, sx * 0.7, 4.5, 5.0, -8.0, -5.6, "dark"))                            # foot pads
    # pistol grip, trigger group
    body += profile([(9.0, 6.2, 4.9, 1.4), (12.0, 6.2, 4.9, 1.4)], "wood")
    body.append(slab(12.6, 5.0, 14.0, 1.6, 1.25, 1.2, "wood", top=False))
    body.append(box(-0.6, 0.6, 1.2, 1.7, 13.3, 15.3, "steel", decal="screw"))                         # grip cap
    body.append(box(-0.2, 0.2, 3.9, 4.95, 9.4, 9.7, "steel"))
    body.append(box(-0.2, 0.2, 3.78, 4.0, 9.6, 12.4, "steel"))
    body.append(box(-0.09, 0.09, 4.05, 4.95, 10.4, 10.7, "steel", rot=[-14, 0, 0], piv=[0, 4.95, 10.55]))
    # stock with cheek piece, rubber recoil pad, swivels
    body += profile([(12.0, 6.95, 4.95, 1.5), (14.5, 6.8, 4.4, 1.5), (20.0, 7.5, 3.4, 1.7), (28.0, 7.4, 1.8, 1.8)], "wood")
    body.append(box(-0.95, 0.95, 1.7, 7.4, 28.0, 28.8, "dark"))
    body.append(box(-0.97, 0.97, 1.6, 1.9, 27.9, 28.9, "steel"))
    body.append(box(0.9, 0.93, 4.0, 5.4, 21.0, 23.4, "brass", decal="crest"))
    body.append(box(0.9, 1.15, 3.2, 3.8, 24.0, 24.5, "steel"))
    body += bolt_rifle_extras(B, 0.0, 9.0, bolt_z=8.6, floor_z=(11.0, 11.3))[:0]
    bolt = rod(B + 0.05, 0.62, 0.4, 9.6, "bright")
    bolt += rod(B - 0.05, 0.5, 9.6, 11.4, "steel")
    bolt += rod(B + 0.05, 0.66, 3.0, 3.4, "steel")                                                    # lug ring
    bolt.append(box(-2.2, -0.4, B - 0.18, B + 0.22, 8.4, 9.2, "bright"))
    bolt += rod(B + 0.02, 0.62, 8.2, 9.4, "bright", x=-2.6)
    return {"main_body": body, "rotate": bolt, "striker": [box(-0.15, 0.15, 6.3, 6.7, 10.6, 11.8, "steel"), box(-0.3, 0.3, 6.2, 6.8, 11.6, 12.2, "bright")],
            "_pivots": {"muzzle_pos": [0, B, muzzle - 0.2], "muzzle_flash": [0, B, muzzle - 1.2],
                        "refit_muzzle_view": [12.35, 7.85, muzzle - 6]}}


def c96():
    """Mauser C96 'broomhandle' on the m1911 rig. Bore y=5.45, sight line y=6.175 (m1911 iron_view)."""
    B, S, muzzle = 5.45, 6.175, -10.4
    gun = []
    gun += rod(B, 0.27, muzzle, -2.0, "steel")
    gun += rod(B, 0.13, muzzle - 0.04, muzzle + 0.1, "dark")
    gun.append(box(-0.06, 0.06, B + 0.2, S, muzzle + 0.25, muzzle + 0.6, "steel"))  # front blade
    gun.append(box(-0.45, 0.45, 4.7, 6.0, -2.2, 2.0, "steel", decal="panel"))    # barrel extension
    gun.append(box(-0.32, 0.32, 5.98, 6.05, -1.9, -0.2, "steel"))                # tangent sight base
    for sx in (-1, 1):
        gun.append(box(sx * 0.07, sx * 0.30, 6.0, S + 0.12, -0.9, -0.6, "steel"))
    gun.append(box(-0.30, 0.30, 6.0, S, -0.9, -0.6, "steel"))
    gun.append(box(-0.40, 0.40, 4.75, 5.9, 2.0, 3.2, "steel"))                   # rear frame
    gun.append(box(-0.12, 0.12, 4.05, 4.75, 2.4, 3.1, "glow"))                   # rune inlay
    # trigger guard
    gun.append(box(-0.18, 0.18, 3.25, 3.45, 0.2, 1.7, "steel"))
    gun.append(box(-0.18, 0.18, 3.25, 4.7, 1.55, 1.75, "steel"))
    lower = [box(-0.40, 0.40, 4.3, 4.75, -2.0, 2.8, "steel")]
    # broomhandle grip: wood, tilted back, lanyard ring
    grip = [box(-0.46, 0.46, 0.2, 4.4, 1.75, 3.25, "wood", rot=[-14, 0, 0], piv=[0, 4.4, 2.4], decal="checkering"),
            box(-0.34, 0.34, 0.2, 4.4, 1.6, 3.4, "wood", rot=[-14, 0, 0], piv=[0, 4.4, 2.4], decal="checkering"),
            box(-0.40, 0.40, 0.0, 0.3, 1.9, 3.1, "steel", rot=[-14, 0, 0], piv=[0, 4.4, 2.4]),
            box(-0.06, 0.06, -0.45, 0.05, 2.75, 3.25, "steel", rot=[-14, 0, 0], piv=[0, 4.4, 2.4])]
    hammer = [box(-0.18, 0.18, 5.2, 6.35, 3.15, 3.45, "steel"), box(-0.18, 0.18, 6.05, 6.35, 3.4, 3.8, "steel")]
    trigger = [box(-0.07, 0.07, 3.55, 4.6, 0.75, 0.95, "steel", rot=[-12, 0, 0], piv=[0, 4.6, 0.85])]
    slide = [box(-0.42, 0.42, 5.75, 6.12, 2.0, 3.15, "bright", decal="ribs")]    # bolt ears
    mag = [box(-0.42, 0.42, 2.6, 4.7, -1.8, 0.2, "steel", decal="panel"), box(-0.46, 0.46, 2.45, 2.7, -1.9, 0.3, "steel")]
    return {"gun": gun, "lower": lower, "grip": grip, "hammer": hammer, "trigger": trigger, "slide": slide,
            "mag_standard": mag,
            "_pivots": {"muzzle_pos": [0, B, muzzle - 0.1], "muzzle_flash": [0, B, muzzle - 1.0]}}


def mp18():
    """Bergmann MP18 on the hk_mp5a5 rig. Bore y=10.875, sight line moved to y=12.0."""
    B, S, muzzle = 10.875, 12.0, -16.0
    gun = []
    gun += rod(B, 0.68, -14.0, -0.6, "steel", decal="holes")  # perforated jacket
    gun += rod(B, 0.30, muzzle, -14.0, "steel")
    gun += rod(B, 0.14, muzzle - 0.04, muzzle + 0.1, "dark")
    gun += rod(B, 0.72, -14.4, -13.8, "steel")
    gun.append(box(-0.07, 0.07, B + 0.6, S, -14.3, -13.9, "steel"))           # front sight
    gun += rod(B + 0.05, 0.66, -0.6, 9.2, "steel")                            # receiver tube
    gun += rod(B + 0.05, 0.68, 0.4, 0.8, "glow")
    gun += rod(B + 0.05, 0.72, 9.0, 9.6, "steel")                             # end cap
    gun.append(box(-0.44, 0.44, B + 0.6, 11.75, 5.6, 6.6, "steel"))           # rear sight base
    for sx in (-1, 1):
        gun.append(box(sx * 0.08, sx * 0.32, 11.75, S + 0.15, 5.9, 6.2, "steel"))
    gun.append(box(-0.32, 0.32, 11.75, S, 5.9, 6.2, "steel"))
    gun.append(box(-0.62, -0.5, 10.6, 11.25, 1.6, 4.4, "dark"))              # ejection port (right)
    gun.append(box(-0.6, 0.6, 9.55, 10.45, -1.5, 1.0, "steel"))              # magazine well
    # wooden stock: fore-stock under the receiver, slim wrist, flared butt
    gun += profile([(0.8, 10.5, 9.4, 1.3), (5.0, 10.5, 8.7, 1.4), (8.8, 10.45, 8.6, 1.4), (10.2, 10.3, 8.9, 1.2),
                    (12.0, 10.35, 8.5, 1.3), (21.6, 10.8, 6.2, 1.6)], "wood")
    gun.append(box(-0.85, 0.85, 6.15, 10.85, 21.6, 22.0, "steel"))
    gun.append(box(0.8, 0.83, 7.8, 8.9, 15.0, 16.8, "brass", decal="crest"))
    gun.append(box(-0.2, 0.2, 8.1, 8.3, 2.0, 4.6, "steel"))                  # trigger guard
    gun.append(box(-0.2, 0.2, 8.1, 8.8, 1.8, 2.05, "steel"))
    gun.append(box(-0.2, 0.2, 8.1, 8.8, 4.4, 4.65, "steel"))
    trigger = [box(-0.08, 0.08, 8.4, 9.3, 3.2, 3.45, "steel", rot=[-12, 0, 0], piv=[0, 9.3, 3.3])]
    handle = [box(-1.15, -0.6, B - 0.1, B + 0.2, 6.5, 7.0, "bright")] + rod(B + 0.05, 0.3, 6.3, 7.2, "bright", x=-1.35)
    bolt = [box(-0.58, -0.45, 10.55, 11.2, 1.9, 4.1, "bright")]
    mag = [box(-0.38, 0.38, 4.9, 9.6, -1.1, 0.6, "steel", rot=[8, 0, 0], piv=[0, 9.6, -0.25], decal="ribs"),
           box(-0.42, 0.42, 4.7, 5.1, -1.2, 0.7, "steel", rot=[8, 0, 0], piv=[0, 9.6, -0.25])]
    return {"body": gun, "trigger": trigger, "bolthandle": handle, "bolt": bolt, "mag2": mag,
            "_pivots": {"muzzle_pos": [0, B, muzzle - 0.1], "muzzle_flash": [0, B, muzzle - 1.0],
                        "iron_view": [0, S, 11], "refit_muzzle_view": [8, 9, muzzle - 5]}}


def trigger_group(z, y_bottom=3.75, y_top=5.0, length=2.6):
    """Steel trigger guard loop and blade with the guard's front at z."""
    return [box(-0.2, 0.2, y_bottom + 0.07, y_top, z - 0.2, z + 0.15, "steel"),
            box(-0.2, 0.2, y_bottom - 0.03, y_bottom + 0.2, z, z + length, "steel"),
            slab(z + length, y_bottom + 0.1, z + length + 1.0, y_top, 0.22, 0.4, "steel", top=False),
            box(-0.09, 0.09, y_bottom + 0.25, y_top, z + 1.0, z + 1.3, "steel", rot=[-14, 0, 0], piv=[0, y_top, z + 1.15])]


def rear_notch(z, base_y, S, w=0.36):
    """Two ears with the notch bottom on the sight line S."""
    out = [box(-w, w, base_y, S, z - 0.2, z + 0.2, "steel")]
    for sx in (-1, 1):
        out.append(box(sx * 0.09, sx * w, S, S + 0.18, z - 0.2, z + 0.2, "steel"))
    return out


def hooded_front(muzzle, B, S, hood=True):
    out = rod(B, 0.4, muzzle + 0.25, muzzle + 1.25, "steel")
    out.append(box(-0.07, 0.07, B + 0.3, S, muzzle + 0.55, muzzle + 0.85, "steel"))
    if hood:
        for sx in (-1, 1):
            out.append(box(sx * 0.25, sx * 0.32, B + 0.25, S + 0.24, muzzle + 0.3, muzzle + 1.15, "steel"))
        out.append(box(-0.32, 0.32, S + 0.18, S + 0.25, muzzle + 0.3, muzzle + 1.15, "steel"))
    return out


def straight_bolt(z, B, length=1.9, knob=0.38, m="bright"):
    """Bolt handle sticking straight out to the right (-X) with a ball knob."""
    return [box(-length, -0.3, B - 0.12, B + 0.2, z - 0.25, z + 0.25, m)] + rod(B + 0.04, knob, z - 0.4, z + 0.4, m, x=-length - 0.3)


def mosin():
    """Mosin-Nagant M1891/30 (Federation): straight bolt, hooded post front sight, straight-wrist stock."""
    B, S, muzzle = 7.25, 8.406, -31.0
    nose = muzzle + 6.5
    body = rod(B, 0.30, muzzle, nose, "steel") + rod(B, 0.36, nose, -6, "steel") + rod(B, 0.42, -6, 0.2, "steel")
    body += rod(B, 0.15, muzzle - 0.05, muzzle + 0.1, "dark") + hooded_front(muzzle, B, S)
    for z in (nose - 0.2, -11.0):  # spring-retained barrel bands with screws
        body.append(box(-0.7, 0.7, 5.85, B + 0.6, z - 0.6, z, "steel", decal="screw"))
    body.append(box(-0.42, 0.42, B + 0.35, 7.95, -5.2, -2.0, "steel"))
    body.append(slab(-4.9, 8.15, -2.3, 7.95, 0.2, 0.62, "steel"))
    body += rear_notch(-4.8, 8.0, S)
    # hexagonal receiver, protruding magazine box, trigger guard
    body.append(box(-0.68, 0.68, 6.5, 7.75, -0.2, 7.6, "steel", decal="serial"))
    body.append(box(-0.5, 0.5, 6.5, 8.0, -0.2, 7.6, "steel"))
    # Mosin recoil cross-bolt pin
    for sx in (-1, 1):
        body.append(box(sx * 0.70, sx * 0.74, 5.7, 6.2, 0.6, 1.2, "steel", decal="screw"))
    body.append(box(-0.46, 0.46, 4.35, 5.2, 1.0, 6.6, "steel", decal="panel"))
    body += trigger_group(6.6)
    body += profile([(nose + 0.6, B - 0.05, 6.2, 1.15), (-11, B - 0.05, 5.9, 1.28), (0.0, 7.05, 5.2, 1.4), (9.0, 7.0, 5.1, 1.5),
                     (11.2, 6.9, 5.0, 1.36), (13.5, 6.55, 4.6, 1.26), (25.6, 6.75, 1.9, 1.6)], "wood")
    body.append(box(-0.5, 0.5, B + 0.2, 7.82, nose + 0.8, -2.2, "wood"))
    body.append(box(-0.84, 0.84, 1.85, 6.85, 25.6, 26.0, "steel", decal="screw"))
    for sx in (-1, 1):  # sling slots through the butt and fore-end
        body.append(box(sx * 0.8, sx * 0.83, 3.2, 3.8, 18.0, 20.0, "dark"))
        body.append(box(sx * 0.62, sx * 0.66, 6.3, 6.8, -15.0, -13.4, "dark"))
    body += bolt_rifle_extras(B, 0.0, 7.6)
    body += rod(B, 0.52, muzzle - 0.2, muzzle + 3.4, "steel")                                  # fixed socket bayonet mount
    body.append(box(-0.5, 0.5, B - 0.12, B + 0.12, muzzle + 0.8, muzzle + 1.3, "dark"))          # bayonet slot
    body += rod(B, 0.60, muzzle + 3.4, muzzle + 3.8, "steel")
    body.append(box(-0.30, 0.30, B + 0.5, B + 0.78, -6.0, -1.0, "steel", decal="ribs"))           # ladder-sight leaf
    bolt = rod(B + 0.05, 0.40, 1.4, 8.9, "bright") + rod(B, 0.33, 8.9, 10.3, "steel")
    bolt += straight_bolt(8.4, B, 1.7)
    return {"main_body": body, "rotate": bolt, "striker": [box(-0.12, 0.12, 6.45, 6.75, 9.9, 10.9, "steel")],
            "_pivots": {"muzzle_pos": [0, B, muzzle - 0.2], "muzzle_flash": [0, B, muzzle - 1.2], "refit_muzzle_view": [12.35, 7.85, muzzle - 6]}}


def lebel():
    """Lebel Mle 1886 (Republic): two-piece stock around a big steel receiver, tube magazine under the barrel."""
    B, S, muzzle = 7.25, 8.406, -33.0
    nose = muzzle + 7.0
    body = rod(B, 0.30, muzzle, nose, "steel") + rod(B, 0.38, nose, 0.0, "steel")
    body += rod(B, 0.15, muzzle - 0.05, muzzle + 0.1, "dark") + hooded_front(muzzle, B, S, hood=False)
    body += rod(5.85, 0.36, nose - 0.3, -0.5, "steel")  # tube magazine, slung under the barrel
    body += rod(5.85, 0.30, nose - 0.7, nose - 0.3, "dark")
    for z in (nose + 1.2, -6.0):                          # tube clamps
        body.append(box(-0.5, 0.5, 5.4, 6.4, z, z + 0.45, "steel", decal="screw"))
    body += rod(5.85, 0.44, -1.3, -0.5, "steel")           # tube / receiver joint
    for z in (nose + 0.2, -12.0):
        body.append(box(-0.7, 0.7, 5.6, B + 0.6, z - 0.7, z, "steel", decal="screw"))
        body.append(box(0.7, 0.84, 5.5, 6.1, z - 0.6, z - 0.1, "steel"))
    body.append(box(-0.45, 0.45, B + 0.35, 7.95, -4.0, -0.6, "steel"))
    body.append(slab(-3.7, 8.2, -0.9, 7.95, 0.24, 0.66, "steel"))
    body += rear_notch(-3.6, 8.0, S)
    # receiver block running down to the trigger guard
    body += rod(B, 0.76, -0.5, 9.0, "steel")                                   # round receiver
    body.append(box(0.46, 0.72, 6.4, 7.9, 0.4, 8.6, "steel", decal="serial"))
    body.append(box(-0.72, -0.46, 6.4, 7.5, 0.4, 8.6, "steel"))
    body.append(box(-0.64, 0.64, 4.6, 6.6, 0.6, 9.6, "steel", decal="panel"))   # lower housing around the lifter
    body.append(box(-0.52, 0.52, 4.2, 4.7, 1.0, 9.0, "steel"))
    body.append(box(-0.66, -0.62, 5.0, 6.2, 2.0, 5.0, "dark"))                  # loading gate
    body.append(box(-0.5, 0.5, 6.4, 7.9, 9.0, 10.4, "steel"))
    body += bolt_rifle_extras(B, 0.0, 9.0, bolt_z=9.1)
    body += trigger_group(6.4, y_bottom=3.55, y_top=4.6)
    # Distinct two-piece stock: fore-end and butt separated by the steel receiver frame
    body += profile([(nose + 0.7, B - 0.1, 6.15, 1.2), (-0.5, B - 0.05, 6.0, 1.36)], "wood")  # fore-end
    body.append(box(-0.5, 0.5, B + 0.2, 7.85, nose + 2.0, -1.0, "wood"))
    # Steel frame side connection screws between wood sections
    for sx in (-1, 1):
        body.append(box(sx * 0.68, sx * 0.73, 4.8, 6.4, 8.8, 10.2, "steel", decal="screw"))
    body += profile([(10.4, 7.0, 4.4, 1.36), (13.5, 6.6, 4.3, 1.26), (26.5, 6.8, 1.9, 1.6)], "wood")  # butt
    body.append(box(-0.84, 0.84, 1.85, 6.9, 26.5, 26.9, "steel", decal="screw"))
    body.append(box(0.8, 0.83, 4.4, 5.6, 20.0, 21.6, "brass", decal="crest"))
    bolt = rod(B + 0.05, 0.42, 0.8, 9.6, "bright") + rod(B, 0.35, 9.6, 11.0, "steel")
    bolt.append(box(-1.6, -0.3, B - 0.12, B + 0.2, 8.6, 9.1, "bright", rot=[0, 0, -15], piv=[-0.3, B, 8.85]))
    bolt += rod(B - 0.45, 0.36, 8.45, 9.25, "bright", x=-1.85)
    return {"main_body": body, "rotate": bolt, "striker": [box(-0.12, 0.12, 6.45, 6.75, 10.4, 11.4, "steel")],
            "_pivots": {"muzzle_pos": [0, B, muzzle - 0.2], "muzzle_flash": [0, B, muzzle - 1.2], "refit_muzzle_view": [12.35, 7.85, muzzle - 6]}}


def lee_enfield():
    """SMLE Mk III (Commonwealth): wood to the muzzle with a blunt nose cap, 10-round box magazine, brass butt."""
    B, S, muzzle = 7.25, 8.406, -25.0
    body = rod(B, 0.30, muzzle - 0.5, muzzle + 0.5, "steel") + rod(B, 0.14, muzzle - 0.55, muzzle - 0.4, "dark")
    body += rod(B, 0.4, muzzle + 0.4, 0.2, "steel")
    body.append(box(-0.7, 0.7, 6.0, 8.15, muzzle + 0.3, muzzle + 1.6, "steel", decal="screw"))  # nose cap
    body.append(box(-0.25, 0.25, 5.3, 6.0, muzzle + 0.3, muzzle + 1.4, "steel"))                # bayonet boss
    for sx in (-1, 1):  # front sight protector ears
        body.append(box(sx * 0.16, sx * 0.3, 8.15, S + 0.15, muzzle + 0.4, muzzle + 1.0, "steel"))
    body.append(box(-0.06, 0.06, 8.15, S, muzzle + 0.55, muzzle + 0.85, "steel"))
    body.append(box(-0.72, 0.72, 5.75, 8.0, -12.6, -12.0, "steel"))  # middle band with swivel
    body.append(box(0.72, 0.84, 5.4, 6.0, -12.5, -12.1, "steel"))
    body.append(box(-0.45, 0.45, 7.9, 8.1, -4.2, -1.4, "steel"))
    body.append(slab(-3.9, 8.25, -1.6, 8.1, 0.18, 0.6, "steel"))
    body += rear_notch(-3.8, 8.1, S)
    body.append(box(-0.66, 0.66, 6.5, 7.9, 0.0, 9.6, "steel", decal="serial"))
    body.append(box(-0.5, 0.5, 4.75, 5.05, 1.0, 6.2, "steel"))
    body += trigger_group(6.2)
    # full-length fore-end and handguard cover the barrel up to the nose cap
    body += profile([(muzzle + 1.6, 8.0, 6.0, 1.25), (-12.6, 8.0, 5.8, 1.3), (-12.0, 8.0, 5.8, 1.3), (0.0, 7.9, 5.2, 1.4)], "wood")
    body.append(box(-0.85, 0.85, 4.6, 7.2, 10.0, 10.8, "steel"))  # butt socket of the two-piece stock
    body += profile([(10.8, 7.0, 4.8, 1.38), (12.6, 6.6, 3.9, 1.3), (13.8, 6.35, 3.7, 1.3), (14.8, 6.3, 4.1, 1.36),
                     (25.4, 6.75, 1.9, 1.62)], "wood")
    body.append(box(-0.85, 0.85, 1.8, 6.85, 25.4, 25.8, "brass", decal="screw"))  # brass butt plate
    body.append(box(-0.84, -0.81, 4.3, 5.5, 17.4, 18.6, "brass", decal="crest"))  # unit disc
    body += sling([(-12.3, 5.75), (6.0, 4.4), (20.5, 3.3)], 0.86)
    body += bolt_rifle_extras(B, 0.0, 9.6, bolt_z=9.4)
    body.append(box(-0.30, 0.30, 7.95, 8.18, -4.0, 3.0, "steel", decal="ribs"))                  # long charger bridge
    body.append(box(-0.56, 0.56, 8.05, 8.4, 3.0, 8.4, "steel"))
    for sx in (-1, 1):                                                                            # volley sight arms
        body.append(box(sx * 0.62, sx * 0.72, 6.6, 7.9, 1.0, 3.0, "steel"))
    mag = [box(-0.42, 0.42, 3.4, 6.3, 1.4, 5.6, "steel", decal="ribs"), box(-0.46, 0.46, 3.3, 3.55, 1.3, 5.7, "steel")]
    bolt = rod(B + 0.05, 0.40, 1.0, 9.4, "bright") + rod(B, 0.32, 9.4, 10.8, "steel")
    bolt.append(box(-1.5, -0.3, B - 0.12, B + 0.2, 9.4, 9.9, "bright"))
    bolt.append(box(-1.9, -1.55, 6.25, B + 0.2, 9.4, 9.9, "bright", rot=[0, 0, -22], piv=[-1.5, B + 0.1, 9.65]))
    bolt += rod(5.95, 0.36, 9.25, 10.05, "bright", x=-2.2)
    return {"main_body": body, "rotate": bolt, "mag_default": mag, "striker": [box(-0.12, 0.12, 6.45, 6.75, 10.4, 11.4, "steel")]}


def luger():
    """Luger P08 on the m1911 rig: toggle lock on top, steeply raked grip. Bore y=5.45, sight line y=6.175."""
    B, S, muzzle = 5.45, 6.175, -7.4
    gun = rod(B, 0.24, muzzle, -1.5, "steel") + rod(B, 0.12, muzzle - 0.04, muzzle + 0.08, "dark")
    gun.append(box(-0.06, 0.06, B + 0.2, S, muzzle + 0.2, muzzle + 0.55, "steel"))
    gun.append(box(-0.42, 0.42, 4.8, 5.85, -1.7, 3.2, "steel", decal="serial"))  # receiver
    gun.append(box(-0.18, 0.18, 3.35, 3.55, -0.4, 1.6, "steel"))                  # round trigger guard
    gun.append(slab(-0.4, 3.55, -0.9, 4.8, 0.2, 0.36, "steel", top=False))
    lower = [box(-0.4, 0.4, 4.35, 4.85, -1.8, 3.4, "steel")]
    grip = [box(-0.44, 0.44, 0.0, 4.45, 1.9, 3.45, "wood", rot=[-30, 0, 0], piv=[0, 4.45, 2.6], decal="checkering"),
            box(-0.36, 0.36, 0.0, 4.45, 1.75, 3.6, "steel", rot=[-30, 0, 0], piv=[0, 4.45, 2.6])]
    trigger = [box(-0.07, 0.07, 3.65, 4.6, 0.55, 0.75, "steel", rot=[-12, 0, 0], piv=[0, 4.6, 0.65])]
    slide = [box(-0.38, 0.38, 5.85, 6.05, 0.6, 2.3, "bright"), box(-0.38, 0.38, 5.85, 6.05, 2.3, 3.4, "bright")]
    for sx in (-1, 1):  # knurled toggle knobs
        slide.append(box(sx * 0.38, sx * 0.62, 5.75, 6.25, 2.15, 2.55, "bright", decal="ribs"))
    slide += rear_notch(3.15, 6.05, S, w=0.3)
    mag = [box(-0.3, 0.3, 0.4, 4.3, 2.1, 3.2, "steel", rot=[-30, 0, 0], piv=[0, 4.45, 2.6]),
           box(-0.36, 0.36, -0.25, 0.4, 2.0, 3.3, "wood", rot=[-30, 0, 0], piv=[0, 4.45, 2.6])]  # wooden base knob
    return {"gun": gun, "lower": lower, "grip": grip, "trigger": trigger, "slide": slide, "mag_standard": mag,
            "_pivots": {"muzzle_pos": [0, B, muzzle - 0.1], "muzzle_flash": [0, B, muzzle - 0.9]}}


def mg08(heavy=False):
    """MG 08/15 light MG (stock + pistol grip) or the heavy MG 08 (fat jacket, spade grips, sled), m249 rig.
    Bore y=8.43, sight line y=11.0 (m249 iron_view)."""
    B, S = 8.43, 11.0
    muzzle = -27.0
    jr = 1.55 if heavy else 1.25
    barrel = rod(B, jr, -24.0, -1.5, "steel", decal="panel")  # water jacket
    barrel += rod(B, jr + 0.1, -24.4, -24.0, "steel") + rod(B, jr + 0.1, -2.0, -1.5, "steel")
    barrel += rod(B, 0.55, muzzle, -24.4, "steel") + rod(B, 0.2, muzzle - 0.05, muzzle + 0.1, "dark")  # muzzle booster
    barrel += yrod(0.0, -6.0, 0.3, B + jr - 0.1, B + jr + 0.25, "brass")  # water filler cap
    if heavy:
        barrel.append(box(1.4, 1.75, B - 0.3, B + 0.3, -12.0, -3.0, "brass"))  # steam hose fitting
    sight2 = [box(-0.35, 0.35, B + jr - 0.1, 10.4, -23.4, -22.4, "steel"), box(-0.06, 0.06, 10.4, S, -23.1, -22.8, "steel")]
    w = 1.2 if heavy else 1.0
    body = [box(-w, w, 6.4, 10.0, -1.5, 11.0, "steel", decal="panel"),
            box(w, w + 0.8, 8.3, 9.6, -0.6, 2.2, "steel"),    # feed block on the left
            box(-w - 0.15, -w, 6.8, 9.6, 2.0, 9.0, "steel")]  # right side plate
    cap = [box(-w, w, 10.0, 10.35, -1.0, 9.0, "steel")]
    rare_sight = [box(-0.4, 0.4, 10.35, 10.6, 8.0, 9.0, "steel")] + rear_notch(8.5, 10.6, S)
    pull = [box(-w - 0.6, -w, 8.2, 8.7, 9.4, 10.2, "bright")] + rod(8.45, 0.32, 9.3, 10.3, "bright", x=-w - 0.85)
    grip2 = [box(-0.5, 0.5, 1.0, 6.4, 6.4, 8.4, "wood", rot=[-14, 0, 0], piv=[0, 6.4, 7.4], decal="ribs")]
    guard = [box(-0.18, 0.18, 3.0, 3.2, 3.6, 6.4, "steel"), box(-0.18, 0.18, 3.0, 6.4, 3.6, 3.85, "steel")]
    trigger = [box(-0.08, 0.08, 4.0, 6.3, 4.8, 5.1, "steel", rot=[-12, 0, 0], piv=[0, 6.3, 4.95])]
    box_ = [box(-1.0, 1.0, 2.6, 6.3, -0.2, 3.2, "steel", decal="panel"), box(-0.15, 0.15, 6.3, 6.8, 0.6, 2.4, "steel")]
    handguard = []
    for sx in (-1, 1):  # folded bipod (08/15) or sled runners (08)
        if heavy:
            handguard.append(box(sx * 0.8, sx * 1.1, 4.4, 4.8, -14.0, 10.0, "steel"))
        else:
            handguard.append(box(sx * 0.35, sx * 0.6, B - jr - 0.4, B - jr - 0.1, -20.0, -6.0, "steel"))
    parts = {"barrel": barrel, "sight2": sight2, "body": body, "cap": cap, "rare_sight": rare_sight, "pull_handle": pull,
             "grip2": grip2, "guard": guard, "trigger": trigger, "box": box_, "handguard": handguard,
             "_keep": {"belt": "cloth", **{f"belt_{k}": "cloth" for k in range(1, 8)}},
             "_pivots": {"muzzle_pos": [0, B, muzzle - 0.2], "muzzle_flash": [0, B, muzzle - 1.2], "refit_muzzle_view": [10, 8, muzzle - 7]}}
    if heavy:  # spade grips and thumb trigger plate at the back instead of a stock
        parts["body"] += [box(-1.3, 1.3, 7.2, 9.6, 11.0, 11.4, "steel")]
        parts["stock"] = [box(sx * 1.0, sx * 1.4, 6.4, 10.0, 11.4, 12.2, "wood", decal="ribs") for sx in (-1, 1)]
        parts["stock"].append(box(-1.0, 1.0, 8.2, 8.6, 11.4, 12.0, "steel"))
    else:
        parts["stock"] = profile([(11.0, 9.7, 5.8, 1.3), (14.0, 9.3, 4.8, 1.2), (23.4, 9.7, 3.2, 1.5)], "wood")
        parts["stock"].append(box(-0.8, 0.8, 3.2, 9.7, 23.4, 23.8, "steel", decal="screw"))
    return parts


def m1897():
    """Winchester M1897 trench gun on the m870 rig: perforated heat shield, bayonet lug, exposed hammer.
    Bore y=9.12; iron_view lowered to a bead on the barrel."""
    B, muzzle = 9.12, -23.25
    S = B + 0.62
    barrel = rod(B, 0.5, muzzle, -4.2, "steel") + rod(B, 0.3, muzzle - 0.05, muzzle + 0.1, "dark")
    barrel += rod(B + 0.05, 0.6, -20.5, -7.0, "steel", decal="holes")  # heat shield
    barrel.append(box(-0.05, 0.05, B + 0.5, S, muzzle + 0.3, muzzle + 0.55, "brass"))  # bead
    barrel.append(box(-0.3, 0.3, B - 0.9, B - 0.4, muzzle + 0.3, muzzle + 2.4, "steel"))  # bayonet lug
    magazine = rod(7.65, 0.46, -15.5, -4.2, "steel")
    group5 = rod(7.65, 0.38, -16.0, -15.5, "steel")
    slide3 = rod(7.6, 0.66, -14.2, -6.4, "wood", decal="ribs")  # corn-cob slide
    body = [box(-0.7, 0.7, 7.1, 9.65, -4.2, 6.2, "steel", decal="serial"),
            slab(6.2, 9.65, 8.4, 9.2, 0.6, 1.3, "steel"),     # rear of the receiver sloping into the wrist
            box(-0.65, 0.65, 6.6, 7.6, 2.0, 8.0, "steel"),    # trigger plate
            box(-0.73, -0.7, 8.2, 9.4, -2.6, 2.2, "dark"),    # ejection port
            box(-0.12, 0.12, 9.2, 10.2, 6.9, 7.3, "steel", rot=[-25, 0, 0], piv=[0, 9.2, 7.1])]  # hammer spur
    trigger = [box(-0.08, 0.08, 5.8, 6.8, 6.4, 6.7, "steel", rot=[-12, 0, 0], piv=[0, 6.8, 6.55])]
    group25 = [box(-0.18, 0.18, 5.4, 5.6, 5.6, 7.9, "steel"), box(-0.18, 0.18, 5.4, 6.8, 7.7, 7.95, "steel")]
    stock = profile([(8.0, 9.2, 6.6, 1.25), (11.0, 8.9, 5.9, 1.2), (22.6, 9.3, 1.8, 1.6)], "wood")
    stock.append(box(-0.82, 0.82, 1.75, 9.35, 22.6, 23.0, "steel", decal="screw"))
    return {"barrel": barrel, "magazine": magazine, "group5": group5, "slide3": slide3, "body": body,
            "trigger": trigger, "group25": group25, "group23": stock, "_shells": True,
            "_pivots": {"iron_view": [0, S, 10], "idle_view": [2.5, 11.6, 13.5]}}


def kampfpistole():
    """Kampfpistole (grenade-firing flare pistol) on the m320 rig: 26.6 mm break-action barrel, raked wooden
    grip, clip-on shoulder stock. Our sights sit on top, so iron_view moves to the bore line."""
    B, Bx = 9.88, 0.0
    S = B + 1.3
    barrel = rod(B, 1.0, -8.8, 3.0, "steel", decal="panel") + rod(B, 0.8, -8.85, -8.6, "dark")
    barrel += rod(B, 1.05, -8.8, -8.2, "steel") + rod(B, 1.05, 2.4, 3.0, "steel")
    barrel.append(box(-0.06, 0.06, B + 1.0, S, -8.1, -7.8, "steel"))  # front blade
    frame = [box(-0.6, 0.6, 8.5, 10.9, 3.0, 4.6, "steel"),
             box(-0.14, 0.14, 10.9, 11.6, 4.1, 4.5, "steel", rot=[-25, 0, 0], piv=[0, 10.9, 4.3])]  # hammer
    frame += rear_notch(3.6, 10.9, S, w=0.32)
    grip = [box(-0.5, 0.5, 4.2, 8.6, 2.4, 4.3, "wood", rot=[-22, 0, 0], piv=[0, 8.6, 3.3], decal="ribs"),
            box(-0.3, 0.3, 7.6, 8.5, 0.6, 2.6, "steel")]  # trigger guard block
    grip.append(box(-0.08, 0.08, 7.0, 8.4, 1.4, 1.7, "steel", rot=[-12, 0, 0], piv=[0, 8.4, 1.55]))
    stock = profile([(4.6, 7.8, 6.8, 0.7), (9.0, 7.9, 6.6, 0.7), (12.4, 8.6, 5.2, 1.1)], "wood")
    stock.append(box(-0.6, 0.6, 4.9, 8.7, 12.4, 12.8, "steel"))
    stock.append(box(-0.25, 0.25, 7.0, 8.2, 4.0, 4.8, "steel"))  # stock clamp
    return {"barrel": barrel, "bone3": frame, "bone2": grip, "stock": stock,
            "_keep": {"head": "olive", "case": "brass"},
            "_pivots": {"iron_view": [Bx, S, 7.96]}}


def m1911():
    """Colt M1911 on the m1911 rig: slide with serrations, dust-cover frame, beavertail, walnut grip panels.
    Bore y=5.45, sight line y=6.175 (m1911 iron_view)."""
    B, S, muzzle = 5.45, 6.175, -6.4
    gun = rod(B, 0.21, muzzle, -4.6, "steel") + rod(B, 0.10, muzzle - 0.03, muzzle + 0.08, "dark")
    gun += rod(B, 0.30, -5.0, -4.5, "steel")                                          # barrel bushing
    gun.append(box(-0.36, 0.36, 4.05, 4.95, -3.8, 3.0, "steel", decal="panel"))       # frame, dust cover and rails
    gun.append(box(-0.30, 0.30, 4.9, 5.1, 2.9, 3.9, "steel"))                         # beavertail grip safety
    gun.append(box(-0.20, 0.20, 3.2, 4.1, -0.5, -0.3, "steel"))                       # trigger guard, front
    gun.append(box(-0.20, 0.20, 3.2, 3.4, -0.5, 1.7, "steel"))
    gun.append(box(-0.20, 0.20, 3.2, 4.1, 1.5, 1.7, "steel"))
    gun.append(box(-0.38, -0.34, 4.35, 4.75, 0.9, 1.9, "steel"))                      # thumb safety lever
    gun.append(box(-0.40, -0.36, 4.1, 4.4, -1.2, -0.4, "dark"))                       # slide stop
    lower = [box(-0.33, 0.33, 3.9, 4.15, -1.2, 3.2, "steel")]
    grip = [box(-0.34, 0.34, 0.2, 4.2, 1.75, 3.2, "steel", rot=[-10, 0, 0], piv=[0, 4.2, 2.4]),            # backstrap
            box(-0.46, -0.30, 0.3, 4.1, 1.85, 3.1, "wood", rot=[-10, 0, 0], piv=[0, 4.2, 2.4], decal="checkering"),
            box(0.30, 0.46, 0.3, 4.1, 1.85, 3.1, "wood", rot=[-10, 0, 0], piv=[0, 4.2, 2.4], decal="checkering"),
            box(-0.36, 0.36, 0.0, 0.25, 1.7, 3.3, "steel", rot=[-10, 0, 0], piv=[0, 4.2, 2.4])]
    trigger = [box(-0.07, 0.07, 3.55, 4.4, 0.35, 0.55, "steel", rot=[-12, 0, 0], piv=[0, 4.4, 0.45])]
    hammer = [box(-0.12, 0.12, 5.1, 5.75, 3.0, 3.35, "steel", rot=[-20, 0, 0], piv=[0, 5.1, 3.1])]
    slide = [box(-0.40, 0.40, 4.95, 5.95, -4.9, 3.2, "steel", decal="serial"),
             box(-0.30, 0.30, 5.95, 6.0, -4.9, 3.2, "steel"),
             box(-0.41, 0.41, 5.05, 5.9, 1.3, 2.9, "steel", decal="vribs"),             # rear serrations
             box(-0.41, 0.41, 5.05, 5.9, -4.8, -3.7, "steel", decal="vribs"),           # front serrations
             box(-0.42, -0.38, 5.4, 5.8, -1.4, 0.2, "dark"),                            # ejection port
             box(-0.06, 0.06, 5.95, S, -4.75, -4.45, "steel")]                          # front blade
    slide += rear_notch(2.95, 5.95, S, w=0.34)
    mag = [box(-0.28, 0.28, 0.5, 4.1, 1.95, 3.0, "steel", rot=[-10, 0, 0], piv=[0, 4.2, 2.4], decal="holes"),
           box(-0.34, 0.34, 0.15, 0.55, 1.85, 3.1, "dark", rot=[-10, 0, 0], piv=[0, 4.2, 2.4])]
    return {"gun": gun, "lower": lower, "grip": grip, "trigger": trigger, "hammer": hammer, "slide": slide,
            "mag_standard": mag, "_pivots": {"muzzle_pos": [0, B, muzzle - 0.1], "muzzle_flash": [0, B, muzzle - 0.9]}}


def springfield():
    """Springfield M1903 on the m700 rig: full-length handguard, stacking swivel, aperture ('peep') rear sight on
    the bridge (its hole centred on the sight line), blued receiver, straight walnut stock."""
    B, S, muzzle = 7.25, 8.406, -28.0
    nose = muzzle + 6.0
    body = rod(B, 0.30, muzzle, nose, "steel") + rod(B, 0.36, nose, -6, "steel") + rod(B, 0.42, -6, 0.2, "steel")
    body += rod(B, 0.15, muzzle - 0.05, muzzle + 0.1, "dark") + hooded_front(muzzle, B, S)
    body.append(box(-0.66, 0.66, 6.1, B + 0.42, nose - 0.5, nose + 0.5, "steel", decal="screw"))   # nose cap
    body += rod(6.2, 0.11, nose - 1.8, nose - 0.3, "steel")                                         # cleaning rod
    for z in (-12.0, -4.8):
        body.append(box(-0.70, 0.70, 5.85, B + 0.55, z - 0.5, z, "steel", decal="screw"))           # barrel bands
    body.append(box(0.70, 0.84, 5.6, 6.2, -12.4, -12.1, "steel"))                                   # stacking swivel
    body.append(box(-0.44, 0.44, B + 0.38, 7.95, -9.0, -6.2, "steel"))                              # rear sight base
    body.append(slab(-8.8, 8.15, -6.4, 7.95, 0.2, 0.6, "steel"))
    body += rear_notch(-8.6, 8.0, S)
    body += rod(B, 0.74, -0.2, 7.9, "steel")                                                       # round receiver
    body.append(box(0.42, 0.70, 6.55, 7.85, 0.0, 6.6, "steel", decal="serial"))
    body.append(box(-0.70, -0.42, 6.55, 7.4, 0.0, 6.6, "steel"))
    for sx in (-1, 1):                                                                             # peep sight posts
        body.append(box(sx * 0.27, sx * 0.43, 7.8, S + 0.5, 7.9, 8.4, "steel"))
    body.append(box(-0.43, 0.43, S + 0.25, S + 0.5, 7.9, 8.4, "steel"))
    body.append(box(-0.43, 0.43, 7.8, S - 0.25, 7.9, 8.4, "steel"))
    body += rod(B + 0.9, 0.12, 6.4, 8.2, "steel")                                                  # sight windage pin
    body.append(box(-0.5, 0.5, 5.05, 5.3, 1.2, 8.6, "steel"))                                      # trigger guard
    body += trigger_group(6.4, y_bottom=3.9, y_top=5.0)
    body += profile([(nose + 0.6, B - 0.05, 6.15, 1.18), (-12.0, B - 0.05, 5.9, 1.30), (0.0, 7.05, 5.2, 1.40),
                     (9.0, 7.0, 4.95, 1.50), (11.5, 6.9, 4.9, 1.38), (13.5, 6.5, 4.3, 1.28), (15.5, 6.35, 4.0, 1.34),
                     (25.4, 6.8, 1.9, 1.62)], "wood")
    body.append(box(-0.5, 0.5, B + 0.2, 7.82, nose + 1.0, -1.4, "wood"))                            # handguard
    body.append(box(-0.84, 0.84, 1.85, 6.85, 25.4, 25.85, "steel", decal="screw"))
    for sx in (-1, 1):
        body.append(box(sx * 0.6, sx * 0.67, 6.4, 6.55, nose + 1.6, -13.0, "groove"))
    body += sling([(-12.2, 5.8), (6.0, 4.4), (20.6, 3.3)], 0.86)
    body += bolt_rifle_extras(B, 0.0, 7.9)
    bolt = rod(B + 0.05, 0.38, 1.4, 8.9, "bright") + rod(B, 0.33, 8.9, 10.3, "steel")
    bolt.append(box(-1.45, -0.3, B - 0.12, B + 0.2, 7.9, 8.5, "bright"))
    bolt.append(box(-1.85, -1.5, 6.25, B + 0.2, 7.9, 8.5, "bright", rot=[0, 0, -22], piv=[-1.45, B + 0.1, 8.2]))
    bolt += rod(5.95, 0.38, 7.75, 8.65, "bright", x=-2.2)
    return {"main_body": body, "rotate": bolt, "striker": [box(-0.12, 0.12, 6.45, 6.75, 9.9, 10.9, "steel")],
            "_pivots": {"muzzle_pos": [0, B, muzzle - 0.2], "muzzle_flash": [0, B, muzzle - 1.2], "refit_muzzle_view": [12.35, 7.85, muzzle - 6]}}


def thompson():
    """Thompson M1928 on the hk_mp5a5 rig: finned barrel with Cutts compensator, vertical foregrip, walnut
    furniture, 20-round stick magazine. Bore y=10.875, sight line y=12.0."""
    B, S, muzzle = 10.875, 12.0, -15.0
    gun = rod(B, 0.30, muzzle, -9.0, "steel") + rod(B, 0.13, muzzle - 0.04, muzzle + 0.1, "dark")
    gun += rod(B, 0.52, muzzle, muzzle + 2.6, "steel")                                  # Cutts compensator
    for k in range(4):
        gun.append(box(-0.56, 0.56, B + 0.28, B + 0.5, muzzle + 0.35 + k * 0.55, muzzle + 0.6 + k * 0.55, "dark"))
    gun.append(box(-0.07, 0.07, B + 0.45, S, muzzle + 0.8, muzzle + 1.1, "steel"))      # front blade
    for k in range(9):                                                                  # cooling fins
        gun += rod(B, 0.72, -9.0 + k * 0.62, -8.6 + k * 0.62, "steel")
    gun += rod(B, 0.5, -3.6, -3.0, "steel")
    gun.append(box(-0.64, 0.64, 9.55, 11.55, -3.6, 8.8, "steel", decal="serial"))      # receiver
    gun.append(box(-0.64, 0.64, 11.55, 11.8, -3.6, 8.8, "steel"))
    gun.append(box(-0.68, -0.64, 10.3, 11.2, 0.2, 2.8, "dark"))                          # ejection port
    gun.append(box(-0.40, 0.40, 11.8, 12.0 - 0.2, 4.6, 6.0, "steel"))                    # rear sight base
    for sx in (-1, 1):
        gun.append(box(sx * 0.09, sx * 0.34, 11.8, S + 0.15, 5.6, 5.95, "steel"))
    gun.append(box(-0.34, 0.34, 11.8, S, 5.6, 5.95, "steel"))
    gun.append(box(-0.6, 0.6, 8.6, 9.6, -2.0, 1.2, "steel"))                              # magazine well
    gun.append(box(-0.6, 0.6, 8.0, 9.4, 1.2, 2.0, "steel"))                               # trigger group
    gun.append(box(-0.2, 0.2, 7.6, 7.85, 1.2, 4.4, "steel"))                              # trigger guard
    gun.append(box(-0.2, 0.2, 7.6, 8.8, 1.2, 1.45, "steel"))
    gun.append(box(-0.2, 0.2, 7.6, 8.8, 4.15, 4.4, "steel"))
    # wood: fore-grip (vertical), pistol grip, stock
    gun.append(box(-0.62, 0.62, 9.55, 10.45, -9.2, -3.6, "wood"))                      # fore-end under the barrel
    gun.append(box(-0.52, 0.52, 6.2, 9.6, -7.9, -6.0, "wood", decal="checkering"))   # vertical foregrip
    gun.append(box(-0.5, 0.5, 5.9, 6.3, -8.0, -5.9, "steel"))                         # its steel cap
    gun.append(box(-0.55, 0.55, 8.2, 9.55, 1.8, 4.6, "wood"))                         # lower receiver wood
    gun.append(box(-0.5, 0.5, 6.0, 8.3, 3.7, 5.1, "wood", rot=[-14, 0, 0], piv=[0, 8.3, 4.3]))   # pistol grip
    gun += profile([(8.8, 10.9, 8.9, 1.2), (12.0, 10.7, 8.5, 1.3), (22.0, 10.9, 6.0, 1.6)], "wood")
    gun.append(box(-0.85, 0.85, 6.0, 10.9, 22.0, 22.4, "steel", decal="screw"))
    trigger = [box(-0.08, 0.08, 7.9, 8.8, 2.7, 2.95, "steel", rot=[-12, 0, 0], piv=[0, 8.8, 2.8])]
    handle = [box(-1.0, -0.6, B + 0.65, B + 0.95, 6.5, 7.0, "bright")] + rod(B + 0.8, 0.3, 6.3, 7.2, "bright", x=-1.2)
    bolt = [box(-0.58, -0.45, 10.3, 10.9, 1.9, 3.9, "bright")]
    mag = [box(-0.36, 0.36, 4.0, 9.6, -1.4, 1.0, "steel", rot=[3, 0, 0], piv=[0, 9.6, -0.2], decal="holes"),
           box(-0.40, 0.40, 3.7, 4.1, -1.5, 1.1, "dark", rot=[3, 0, 0], piv=[0, 9.6, -0.2])]
    return {"body": gun, "trigger": trigger, "bolthandle": handle, "bolt": bolt, "mag2": mag,
            "_pivots": {"muzzle_pos": [0, B, muzzle - 0.1], "muzzle_flash": [0, B, muzzle - 1.0],
                        "iron_view": [0, S, 11], "refit_muzzle_view": [8, 9, muzzle - 5]}}


def bar_m1918():
    """Browning Automatic Rifle M1918 on the rpk rig: slotted flash hider, gas cylinder, full walnut fore-end,
    20-round box magazine, pistol grip and stock. Bore y=8.556, sight line y=10.919 (rpk iron_view)."""
    B, S, muzzle = 8.556, 10.919, -27.7
    barrel = rod(B, 0.36, muzzle + 3.4, -12.0, "steel") + rod(B, 0.5, muzzle, muzzle + 3.4, "steel")
    barrel += rod(B, 0.2, muzzle - 0.03, muzzle + 0.1, "dark")
    for k in range(3):
        barrel.append(box(-0.56, 0.56, B - 0.12, B + 0.12, muzzle + 0.5 + k * 0.9, muzzle + 0.9 + k * 0.9, "dark"))
    barrel.append(box(-0.5, 0.5, B + 0.4, B + 1.2, -26.4, -24.4, "steel"))                      # front sight base
    barrel.append(box(-0.07, 0.07, B + 1.2, S, -25.8, -25.4, "steel"))
    for sx in (-1, 1):
        barrel.append(box(sx * 0.3, sx * 0.4, B + 1.1, S + 0.25, -26.0, -25.2, "steel"))
    gas = rod(B - 1.0, 0.30, -23.5, -8.0, "steel") + rod(B - 1.0, 0.38, -24.0, -23.4, "steel")  # gas cylinder
    gas.append(box(-0.3, 0.3, B - 0.8, B - 0.2, -24.0, -20.0, "steel"))
    wood = profile([(-22.0, B - 0.1, B - 1.9, 1.5), (-8.0, B + 0.15, B - 2.1, 1.6), (-2.5, B + 0.25, B - 2.2, 1.7)], "wood")
    wood.append(box(-0.9, 0.9, B + 0.1, B + 0.5, -21.5, -5.0, "wood"))                         # handguard top
    wood.append(box(-0.85, 0.85, B - 2.4, B - 1.9, -12.5, -11.8, "steel", decal="screw"))     # fore-end band
    lower = [box(-0.74, 0.74, 6.2, 9.7, -3.0, 13.0, "steel", decal="serial"),                   # receiver
             box(-0.78, -0.72, 7.5, 9.3, 0.5, 6.0, "dark"),                                      # ejection port
             box(-0.6, 0.6, 9.7, 10.15, -3.0, 13.0, "steel"),
             box(-0.72, 0.72, 4.8, 6.2, -1.0, 5.2, "steel"),                                     # magazine well
             box(-0.2, 0.2, 5.0, 5.2, 5.4, 10.4, "steel"), box(-0.2, 0.2, 5.0, 6.4, 5.2, 5.45, "steel"),
             box(-0.2, 0.2, 5.0, 6.4, 10.2, 10.45, "steel"),                                     # trigger guard
             box(-0.4, 0.4, 10.15, 10.55, 6.0, 7.6, "steel")]                                    # rear sight base
    for sx in (-1, 1):
        lower.append(box(sx * 0.09, sx * 0.36, 10.55, S + 0.2, 6.5, 6.9, "steel"))
    lower.append(box(-0.36, 0.36, 10.55, S, 6.5, 6.9, "steel"))
    lower += profile([(13.0, 9.6, 6.9, 1.4), (15.5, 9.4, 5.4, 1.4), (26.0, 9.9, 2.4, 1.7)], "wood")   # stock
    lower.append(box(-0.9, 0.9, 2.3, 9.9, 26.0, 26.5, "steel", decal="screw"))
    grip = [box(-0.5, 0.5, 3.2, 6.4, 8.8, 10.4, "wood", rot=[-16, 0, 0], piv=[0, 6.4, 9.3], decal="checkering")]
    trigger = [box(-0.08, 0.08, 4.9, 6.2, 7.0, 7.3, "steel", rot=[-12, 0, 0], piv=[0, 6.2, 7.15])]
    bolt = [box(-0.55, 0.55, 8.4, 9.5, 0.6, 6.2, "bright")] + [box(-0.9, -0.55, 8.5, 9.0, 3.4, 4.2, "bright")]
    mag = [box(-0.5, 0.5, 1.0, 5.2, 0.4, 4.4, "steel", rot=[6, 0, 0], piv=[0, 5.2, 2.4], decal="ribs"),
           box(-0.56, 0.56, 0.7, 1.1, 0.3, 4.5, "dark", rot=[6, 0, 0], piv=[0, 5.2, 2.4])]
    return {"barrel3": barrel, "gastube2": gas, "wood2": wood, "lower2": lower, "grip2": grip, "trigger2": trigger,
            "bolt": bolt, "mag2": mag, "_pivots": {"muzzle_pos": [0, B, muzzle - 0.2], "muzzle_flash": [0, B, muzzle - 1.2]}}


GUNS = {  # id -> (donor, builder)
    "kar98k": ("m700", lambda: mauser_rifle(-25.0)),
    "gewehr98": ("m700", lambda: {**mauser_rifle(-31.0, gew=True),
                                   "_pivots": {"muzzle_pos": [0, 7.25, -31.2], "muzzle_flash": [0, 7.25, -32.2],
                                               "refit_muzzle_view": [12.35, 7.85, -37]}}),
    "t_gewehr": ("m700", t_gewehr),
    "c96": ("m1911", c96),
    "mp18": ("hk_mp5a5", mp18),
    "luger_p08": ("m1911", luger),
    "mosin": ("m700", mosin),
    "lebel": ("m700", lebel),
    "lee_enfield": ("m700", lee_enfield),
    "mg08_15": ("m249", mg08),
    "mg08": ("m249", lambda: mg08(heavy=True)),
    "m1897": ("m870", m1897),
    "kampfpistole": ("m320", kampfpistole),
    "m1911": ("m1911", m1911),
    "springfield": ("m700", springfield),
    "thompson": ("hk_mp5a5", thompson),
    "bar_m1918": ("rpk", bar_m1918),
}
BULLET_BONES = {"bullet", "bullet2", "bullet3", "bullet4", "bullet5", "bullet_in_mag", "bullet_in_chamber",
                "bullet_in_barrel", "bullet_shell", "bullet_shell2", "head"}

# ---------------------------------------------------------------- geo assembly

def build_geo(gun_id, donor_name, parts):
    with zipfile.ZipFile(JAR) as z:
        donor = json.loads(z.read(DONOR.format(donor_name)))
    g = donor["minecraft:geometry"][0]
    pivots = parts.pop("_pivots", {})
    keep = parts.pop("_keep", {})      # bone -> material: reuse the donor's cube shapes (belts, grenades)
    shells = parts.pop("_shells", False)  # shotgun: rounds are paper shells, not bullets
    names = {b["name"] for b in g["bones"]}
    missing = set(parts) - names
    assert not missing, f"{gun_id}: unknown bones {missing}"
    bones = []
    for b in g["bones"]:
        nb = {k: v for k, v in b.items() if k != "cubes"}
        if b["name"] in pivots:
            nb["pivot"] = pivots[b["name"]]
        cubes = list(parts.get(b["name"], []))
        keep_as = keep.get(b["name"], "brass" if b["name"].isdigit() else None)  # m249 numbers its belt rounds
        if keep_as and b.get("cubes"):
            cubes += [donor_cube(c, keep_as) for c in b["cubes"]]
        elif b["name"] in BULLET_BONES and b.get("cubes"):
            lo = [min(c["origin"][i] for c in b["cubes"]) for i in range(3)]
            hi = [max(c["origin"][i] + c["size"][i] for c in b["cubes"]) for i in range(3)]
            if shells:
                cubes += shotshell(lo, hi)
            else:
                cubes += cartridge(lo, hi, tip=b["name"] not in ("bullet_shell", "bullet_shell2"))
        if b["name"] == "head" and donor_name == "m700":  # m700 splits the chambered round into head + case
            cubes = [dict(c, m="copper") for c in cubes]
        nb["_cubes"] = cubes
        bones.append(nb)
    return donor, bones


def donor_cube(c, m):
    out = {"o": list(c["origin"]), "s": list(c["size"]), "m": m}
    if c.get("rotation"):
        out["rot"], out["piv"] = c["rotation"], c["pivot"]
    return out


def face_dims(c):
    w, h, d = c["s"]
    dims = {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h), "up": (w, d), "down": (w, d)}
    for f in c.get("hide", ()):  # buried faces get a single texel instead of a full texture rect
        dims[f] = (1.0 / P, 1.0 / P)
    return dims


def pack(bones):
    """Shelf-pack every face; returns texture size. Each face gets its own texel rect."""
    faces = []
    for b in bones:
        for c in b["_cubes"]:
            c["faces"] = {}
            for f, (fw, fh) in face_dims(c).items():
                tw, th = max(1, math.ceil(fw * P - 1e-6)), max(1, math.ceil(fh * P - 1e-6))
                faces.append((th, tw, c, f, fw * P, fh * P))
    faces.sort(key=lambda t: (-t[0], -t[1]))
    for size in (512, 1024, 2048):
        x = y = row = 0
        ok = True
        for th, tw, c, f, uw, vh in faces:
            if x + tw + 1 > size:
                x, y, row = 0, y + row + 1, 0
            if y + th > size:
                ok = False
                break
            c["faces"][f] = (x, y, tw, th, uw, vh)
            x += tw + 1
            row = max(row, th)
        if ok:
            return size
    raise SystemExit("atlas overflow")


def geo_json(donor, bones, tex):
    out = []
    for b in bones:
        nb = {k: v for k, v in b.items() if k != "_cubes"}
        if b["_cubes"]:
            nb["cubes"] = []
            for c in b["_cubes"]:
                uv = {}
                for f, (x, y, tw, th, uw, vh) in c["faces"].items():
                    uv[f] = {"uv": [x, y + vh], "uv_size": [round(uw, 4), round(-vh, 4)]} if f == "down" else \
                            {"uv": [x, y], "uv_size": [round(uw, 4), round(vh, 4)]}
                e = {"origin": [round(v, 4) for v in c["o"]], "size": [round(v, 4) for v in c["s"]], "uv": uv}
                if "rot" in c:
                    e["pivot"], e["rotation"] = [round(v, 4) for v in c["piv"]], [round(v, 3) for v in c["rot"]]
                nb["cubes"].append(e)
        out.append(nb)
    d = dict(donor["minecraft:geometry"][0]["description"])
    d.update(texture_width=tex, texture_height=tex)
    return {"format_version": "1.12.0", "minecraft:geometry": [{"description": d, "bones": out}]}

# ---------------------------------------------------------------- texture

def h2(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2246822519) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return (n ^ (n >> 16)) / 0xffffffff


def vnoise(x, y, sx, sy, s):
    gx, gy = x / sx, y / sy
    x0, y0 = math.floor(gx), math.floor(gy)
    fx, fy = gx - x0, gy - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b, c, d = h2(x0, y0, s), h2(x0 + 1, y0, s), h2(x0, y0 + 1, s), h2(x0 + 1, y0 + 1, s)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def mul(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


WOODS = {  # name -> (dark, mid, light) of the grain
    "wood": ((36, 23, 16), (98, 65, 43), (142, 98, 66)),     # dark oiled walnut
    "beech": ((86, 56, 34), (142, 100, 64), (184, 140, 94)),  # lighter beech / birch service stock
}
STEEL = (44, 49, 60)        # blued steel: blue-black, the highlights do the rest
BRIGHT = (176, 180, 186)
BRASS = (206, 160, 68)
COPPER = (184, 102, 64)
GLOW = (110, 235, 255)


def texel(m, f, i, j, fw, fh, gx, gy, seed, world=None):
    """Colour of texel (i, j) on a face of fw x fh texels. Grain/brushing runs along the gun (world Z).
    world = (along, across) in model units; wood uses it so the grain flows across cube seams."""
    along, across = (i, j) if f in ("east", "west") else (j, i) if f in ("up", "down") else (i, j)
    edge = min(i, j, fw - 1 - i, fh - 1 - j)
    side = f not in ("up", "down")
    vert = j / max(1, fh - 1) if side else 0.3  # 0 = top of a side face

    wz, wy, wx = None, None, None
    if world:
        if f in ("east", "west"):
            wz, wy = world[0], world[1]
        elif f in ("up", "down"):
            wz, wx = world[0], world[1]
        elif f in ("north", "south"):
            wx, wy = world[0], world[1]

    if m in WOODS:
        dark, mid, light = WOODS[m]
        if f in ("north", "south"):  # end grain: dark growth rings
            r = math.hypot(i - fw / 2, (j - fh / 2) * 1.4)
            k = 0.5 + 0.28 * math.sin(r * 1.5 + vnoise(i, j, 3, 3, seed) * 3.0)
            col = mix(dark, mid, k * 0.8)
        else:
            wa = wz * P if wz is not None else along
            wc = (wy * P if wy is not None else wx * P if wx is not None else across)
            warp = vnoise(wa, wc, 70, 14, 5) * 7.0 + vnoise(wa, wc, 22, 5, 6) * 1.6
            ring = 0.5 + 0.5 * math.sin((wc + warp) * 0.7)           # long flame / cathedral grain lines
            fibre = vnoise(wa, wc, 48, 1.3, 9)                          # very long fibres
            fine = vnoise(wa, wc, 14, 0.9, 11)
            cloud = vnoise(wa, wc, 60, 30, 8)                           # broad colour clouds
            k = 0.30 + 0.30 * ring * (0.6 + 0.5 * fibre) + 0.22 * (cloud - 0.5) + 0.20 * (fine - 0.5)
            col = mix(dark, mid, k * 1.6) if k < 0.62 else mix(mid, light, (k - 0.62) * 2.2)
            if h2(int(wa) // 5, int(wc), 7) < 0.02:                     # open pores
                col = mul(col, 0.62)
            if h2(int(wa) // 14, int(wc) // 2, 13) < 0.006:             # dents and scratches
                col = mul(col, 1.35 if h2(int(wa), int(wc), 3) > 0.5 else 0.7)
            if wz is not None:  # hand polish at the wrist and fore-end: darker, glossier
                if 9.5 <= wz <= 15.0:
                    col = mix(mul(dark, 1.2), col, 0.62 + 0.38 * min(1.0, abs(wz - 12.2) / 2.8))
                elif -14.0 <= wz <= 3.0 and wy is not None and wy < 6.8:
                    col = mix(mul(dark, 1.3), col, 0.78)
        if f == "up":  # oil sheen: a soft lighter band down the middle of the top face
            col = mul(col, 1.10 + 0.18 * math.exp(-((i / max(1, fw - 1) - 0.5) / 0.22) ** 2))
        elif f == "down":
            col = mul(col, 0.7)
        else:
            col = mul(col, 1.08 - 0.32 * vert)
        # rounded-over long edges only (not the ends of segments, which would show seams in a smoothed stock)
        if side and min(fw, fh) >= 3 and (j == 0 or j == fh - 1):
            col = mul(col, 1.18 if j == 0 else 0.72)
        elif f in ("up", "down") and min(fw, fh) >= 3 and (i == 0 or i == fw - 1):
            col = mul(col, 1.1 if f == "up" else 0.7)

    elif m in ("steel", "dark"):
        base = STEEL if m == "steel" else (21, 22, 25)
        sk = 0.55 + 0.45 * (1.0 - vert) if side else 0.95  # underside falls into shadow
        col = mul(base, sk)
        # fake environment reflection: soft light band on the shoulder of side faces, centre line on top faces
        if m == "steel":
            if side:
                spec = math.exp(-((vert - 0.16) / 0.10) ** 2) * 0.55 + math.exp(-((vert - 0.55) / 0.25) ** 2) * 0.10
            else:
                spec = math.exp(-((i / max(1, fw - 1) - 0.5) / 0.20) ** 2) * 0.45
            col = (min(255, int(col[0] + spec * 70)), min(255, int(col[1] + spec * 80)), min(255, int(col[2] + spec * 104)))
        col = mul(col, 0.94 + 0.12 * vnoise(along, across, 20, 1.6, seed))   # machining streaks along the bore
        col = mul(col, 1.0 + (h2(i, j, seed) - 0.5) * 0.10)                   # grain
        # blued steel fades to plum-brown where it is handled; oil stains pool low
        patch = vnoise(world[0] * P if world else along, world[1] * P if world else across, 38, 22, seed + 3)
        if patch > 0.62:
            col = mix(col, (74, 58, 52), (patch - 0.62) * 1.1)
        # bare-metal edge wear on the high points, dark crease on the lower edges
        if m == "steel" and min(fw, fh) >= 6 and edge == 0:
            top_edge = (f == "up") or (side and j == 0)
            if h2(i, j, seed + 17) > (0.2 if top_edge else 0.55):
                col = mix(col, (176, 180, 188), 0.62 if top_edge else 0.32)
            elif not top_edge:
                col = mul(col, 0.6)
        elif m == "steel" and min(fw, fh) >= 6 and edge == 1 and (f == "up" or (side and j == 1)):
            col = mix(col, (110, 116, 128), 0.22)

    elif m == "bright":  # polished bolt body, handle, extractor
        col = mul(BRIGHT, 1.12 - 0.30 * vert)
        col = mul(col, 0.93 + 0.14 * vnoise(along, across, 6, 1, seed))
        if side:
            col = mul(col, 1.0 + 0.25 * math.exp(-((vert - 0.2) / 0.12) ** 2))
        if edge == 0:
            col = mul(col, 0.74)

    elif m == "olive":  # painted grenade body
        col = mul((86, 92, 58), 1.1 - 0.3 * vert)
        col = mul(col, 0.92 + 0.12 * vnoise(along, across, 4, 4, seed))
        if edge == 0:
            col = mix(col, (120, 122, 115), 0.3)

    elif m == "cloth":  # canvas ammo belt
        col = mul((150, 132, 96), 1.05 - 0.2 * vert)
        if (i + j) % 3 == 0:
            col = mul(col, 0.88)
        if (i - j) % 4 == 0:
            col = mul(col, 0.94)

    elif m == "red":  # paper shotgun hull
        col = mul((150, 34, 30), 1.1 - 0.3 * vert)
        if j % 3 == 0 and side:
            col = mul(col, 0.9)

    elif m == "groove":
        col = (38, 18, 8)

    elif m == "leather":
        col = mul((96, 60, 36), 1.08 - 0.22 * vert)
        col = mul(col, 0.9 + 0.18 * vnoise(along, across, 4, 4, seed))
        if edge == 0:
            col = mul(col, 0.65)
        elif edge == 1 and side and fh >= 4:
            if (i if along == i else j) % 3 == 0:
                col = (185, 170, 130)  # stitched wax thread
            else:
                col = mul(col, 1.12)

    elif m == "brass":
        col = mul(BRASS, 1.16 - 0.32 * vert)
        col = mul(col, 0.96 + 0.08 * vnoise(along, across, 8, 2, seed))
        if edge == 0:
            col = mul(col, 0.78)

    elif m == "copper":
        col = mul(COPPER, 1.12 - 0.28 * vert)
        col = mul(col, 0.96 + 0.08 * vnoise(along, across, 6, 2, seed))

    elif m == "glow":  # elenium rune band: bright core, glyph ticks
        core = 1.0 - abs(j - (fh - 1) / 2) / max(1, fh / 2)
        col = mix((36, 145, 185), (235, 255, 255), core)
        if side and fw > 6 and (i % 6 in (0, 1)) and h2(i // 6, 0, seed) < 0.5:
            col = (255, 255, 255)
    else:
        col = (255, 0, 255)
    return col


DIGITS = {"1": ["010", "110", "010", "010", "111"], "9": ["111", "101", "111", "001", "111"],
          "3": ["111", "001", "111", "001", "111"], "8": ["111", "101", "111", "101", "111"]}


def decal(kind, put, fw, fh, seed):
    if kind == "crest" and fw >= 6 and fh >= 4:  # engraved eagle-ish crest on a brass plate
        cx, cy = fw // 2, fh // 2
        for i in range(fw):
            for j in range(fh):
                if i in (0, fw - 1) or j in (0, fh - 1):
                    put(i, j, (120, 88, 36))
        for k in range(-3, 4):
            put(cx + k, cy - abs(k) // 2, (110, 80, 30))
        for k in range(-1, 3):
            put(cx, cy + k, (110, 80, 30))
    elif kind == "holes":  # rows of oval cooling holes on the jacket
        for i in range(2, fw - 3, 7):
            for j in range(2, fh - 2, 5):
                for di in range(4):
                    for dj in range(2):
                        put(i + di, j + dj, (14, 14, 16))
    elif kind == "ribs":  # grip grooves / magazine ribs across the long axis
        for j in range(1, fh - 1, 3):
            for i in range(fw):
                put(i, j, None)
    elif kind == "vribs":  # vertical serrations
        for i in range(1, fw - 1, 2):
            for j in range(1, fh - 1):
                put(i, j, None)
    elif kind == "checkering":  # fine diamond checkering on walnut or grips
        for j in range(1, fh - 1):
            for i in range(1, fw - 1):
                if (i + j) % 3 == 0 or (i - j) % 3 == 0:
                    put(i, j, None)
    elif kind == "screw" and fw >= 4 and fh >= 4:  # slotted screw head in the middle of the face
        cx, cy, r = fw // 2, fh // 2, max(2, min(fw, fh) // 3)
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                if i * i + j * j <= r * r:
                    put(cx + i, cy + j, (132, 136, 144) if i * i + j * j < (r - 1) ** 2 else (26, 28, 32))
        for i in range(-r + 1, r):
            put(cx + i, cy, (18, 18, 22))
    elif kind == "serial" and fw >= 20 and fh >= 7:  # stamped proof marks and serial number
        y0 = fh // 2 - 2
        for n, ch in enumerate("1938"):
            for r_, row in enumerate(DIGITS[ch]):
                for c_, bit in enumerate(row):
                    if bit == "1":
                        put(3 + n * 4 + c_, y0 + r_, (155, 160, 168))
        for k in range(3):  # small eagle proof stamps
            cx = fw - 6 - k * 5
            put(cx, y0 + 1, (155, 160, 168)); put(cx - 1, y0, (155, 160, 168)); put(cx + 1, y0, (155, 160, 168))
            put(cx, y0 + 2, (155, 160, 168))
    elif kind == "groove":  # finger groove along a fore-end side
        for i in range(2, fw - 2):
            put(i, fh // 2, (38, 18, 8))
            put(i, fh // 2 + 1, None)
    elif kind == "panel":  # milled recess outline
        for i in range(2, fw - 2):
            for j in (2, fh - 3):
                put(i, j, (22, 24, 28))
        for j in range(2, fh - 2):
            for i in (2, fw - 3):
                put(i, j, (22, 24, 28))


def paint(bones, size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    for bi, b in enumerate(bones):
        for ci, c in enumerate(b["_cubes"]):
            seed = bi * 131 + ci * 7
            (ox, oy, oz), (sx, sy, sz) = c["o"], c["s"]
            for f, (x0, y0, tw, th, uw, vh) in c["faces"].items():
                for j in range(th):
                    for i in range(tw):
                        u, v = (i + 0.5) / P, (j + 0.5) / P
                        world = {"east": (oz + sz - u, oy + sy - v), "west": (oz + u, oy + sy - v),
                                 "up": (oz + v, ox + u), "down": (oz + v, ox + u),
                                 "north": (ox + u, oy + sy - v), "south": (ox + sx - u, oy + sy - v)}.get(f)
                        col = texel(c["m"], f, i, j, tw, th, x0 + i, y0 + j, seed, world)
                        px[x0 + i, y0 + j] = col + (255,)
                if f in ("east", "west", "north", "south") and c.get("decal"):
                    def put(i, j, col, x0=x0, y0=y0, tw=tw, th=th):
                        if 0 <= i < tw and 0 <= j < th:
                            px[x0 + i, y0 + j] = (mul(px[x0 + i, y0 + j][:3], 0.55) if col is None else col) + (255,)
                    decal(c["decal"], put, tw, th, seed)
    return img

# ---------------------------------------------------------------- pack json

DONOR_JSON = "assets/tacz/custom/tacz_default_gun/{}"
SOUNDS_FROM = {"kar98k": "m700", "gewehr98": "m700", "t_gewehr": "m95", "c96": "m1911", "mp18": "hk_mp5a5",
               "luger_p08": "glock_17", "mosin": "m700", "lebel": "springfield1873", "lee_enfield": "m700", "mg08_15": "m249", "mg08": "m249", "m1897": "m870", "kampfpistole": "m320",
               "m1911": "m1911", "springfield": "m700", "thompson": "ump45", "bar_m1918": "rpk"}
DISPLAY_EXTRA = {}  # gun id -> display fields to override
TRACER = {"kar98k": "#FFE6A0", "gewehr98": "#FFE6A0", "t_gewehr": "#FFE6A0", "mosin": "#FFE6A0", "lebel": "#FFE6A0",
          "lee_enfield": "#FFE6A0", "mg08": "#FFE6A0", "mg08_15": "#FFE6A0", "springfield": "#FFE6A0", "thompson": "#FFE6A0",
          "bar_m1918": "#FFE6A0", "m1911": "#FFE6A0", "c96": "#FFE6A0", "mp18": "#FFE6A0", "luger_p08": "#FFE6A0", "m1897": "#FFD08A"}  # rifles take the tracer colour from their youjoarms ammo


def donor_json(z, path):
    text = z.read(DONOR_JSON.format(path)).decode("utf-8")
    return json.loads(re.sub(r"^\s*//.*$", "", text, flags=re.M))


def write_display(z, gun_id, donor_name):
    """Display = the donor's (animation, state machine, shells, view offsets) with our model, art and sounds."""
    d = donor_json(z, f"assets/tacz/display/guns/{donor_name}_display.json")
    d.update(model=f"youjoarms:gun/{gun_id}_geo", texture=f"youjoarms:gun/uv/{gun_id}",
             lod={"model": f"youjoarms:gun/{gun_id}_geo", "texture": f"youjoarms:gun/uv/{gun_id}"},
             hud=f"youjoarms:gun/hud/{gun_id}", slot=f"youjoarms:gun/slot/{gun_id}")
    d["sounds"] = donor_json(z, f"assets/tacz/display/guns/{SOUNDS_FROM[gun_id]}_display.json")["sounds"]
    d.pop("ammo", None)  # m700 ships a debug mycelium particle trail on its rounds
    d.update(DISPLAY_EXTRA.get(gun_id, {}))
    if gun_id in TRACER:
        d["tracer_color"] = TRACER[gun_id]
    os.makedirs(f"{PACK}/display/guns", exist_ok=True)
    json.dump(d, open(f"{PACK}/display/guns/{gun_id}_display.json", "w"), indent=2)

# ---------------------------------------------------------------- icons

def icon(geo, tex, w, h, yaw=90, pitch=0, outline=True):
    """Side-view render on a transparent background (inventory slot / HUD art)."""
    qs = list(preview_geo.quads(geo, tex, {"lefthand_pos", "righthand_pos"}))
    big = preview_geo.render(qs, yaw, pitch, w * 4, h * 4, light=(0.3, 0.9, 0.3))
    bg = big.getpixel((0, 0))
    mask = Image.new("L", big.size, 0)
    bp, mp = big.load(), mask.load()
    for y in range(big.height):
        for x in range(big.width):
            if bp[x, y] != bg:
                mp[x, y] = 255
    rgba = big.convert("RGBA")
    rgba.putalpha(mask)
    out = rgba.resize((w, h), Image.LANCZOS)
    if outline:  # dark 1px outline so the icon reads on any slot background
        a = out.split()[3].point(lambda v: 255 if v > 90 else 0)
        grown = a.filter(ImageFilter.MaxFilter(3))
        shadow = Image.new("RGBA", out.size, (16, 14, 12, 255))
        shadow.putalpha(grown)
        shadow.alpha_composite(out)
        out = shadow
    return out


def main():
    os.makedirs(f"{PACK}/geo_models/gun", exist_ok=True)
    for sub in ("uv", "slot", "hud"):
        os.makedirs(f"{PACK}/textures/gun/{sub}", exist_ok=True)
    z = zipfile.ZipFile(JAR)
    for gun_id, (donor_name, builder) in GUNS.items():
        write_display(z, gun_id, donor_name)
        donor, bones = build_geo(gun_id, donor_name, builder())
        size = pack(bones)
        geo = geo_json(donor, bones, size)
        tex = paint(bones, size)
        json.dump(geo, open(f"{PACK}/geo_models/gun/{gun_id}_geo.json", "w"), indent=1)
        tex.save(f"{PACK}/textures/gun/uv/{gun_id}.png")
        icon(geo, tex, 64, 64).save(f"{PACK}/textures/gun/slot/{gun_id}.png")
        icon(geo, tex, 384, 128, outline=False).save(f"{PACK}/textures/gun/hud/{gun_id}.png")
        n = sum(len(b["_cubes"]) for b in bones)
        print(f"{gun_id:10} donor={donor_name:9} cubes={n:4} texture={size}")


if __name__ == "__main__":
    main()
