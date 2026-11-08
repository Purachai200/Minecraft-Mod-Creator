#!/usr/bin/env python3
"""Vehicle Fleet generator: geo + animation + 1024 atlas + SPECS.md for all four vehicles.

Run:  python scripts/gen_fleet.py [technical hauler mi17 freighter] [--preview DIR]
Needs ../Titan Combat/scripts (cube helpers, atlas painter, software renderer).
"""
import copy, json, os, shutil, sys
from fleet_common import *
import fleet_ground as G
import lights as L

PAINT = {"technical_4x4": dict(rust=0.5, seed=11), "ural_6x6": dict(rust=0.8, seed=12),
         "mi17_hip": dict(rust=0.45, seed=13), "coaster_freighter": dict(rust=1.2, seed=14),
         "mi26_halo": dict(rust=0.5, seed=15), "recovery_6x6": dict(rust=0.6, seed=16),
         "fac_patrol": dict(rust=0.9, seed=19), "opv_cutter": dict(rust=0.8, seed=20), "corvette_stealth": dict(rust=0.6, seed=21),
         "lpd_assault": dict(rust=0.8, seed=22), "transport_sub": dict(rust=0.5, seed=23), "c17_airlifter": dict(rust=0.4, seed=24),
         "humvee_m1165": dict(rust=0.4, seed=17), "uh60_blackhawk": dict(rust=0.35, seed=18)}


def registry():
    reg = {"technical": (G.technical, G.technical_anims), "hauler": (G.hauler, G.hauler_anims)}
    try:
        import fleet_mi17 as M; reg["mi17"] = (M.mi17, M.mi17_anims)
    except ImportError: pass
    try:
        import fleet_freighter as F; reg["freighter"] = (F.freighter, F.freighter_anims)
    except ImportError: pass
    try:
        import fleet_heavy as Hv; reg["mi26"] = (Hv.mi26, Hv.mi26_anims); reg["recovery"] = (Hv.recovery, Hv.recovery_anims)
    except ImportError: pass
    try:
        import fleet_us as U; reg["humvee"] = (U.humvee, U.humvee_anims); reg["blackhawk"] = (U.blackhawk, U.blackhawk_anims)
    except ImportError: pass
    try:
        import fleet_ships as S
        for k, fn in (("fac", S.fac), ("opv", S.opv), ("corvette", S.corvette)):
            reg[k] = (fn, S.ships_anims({"fac": "fac_patrol", "opv": "opv_cutter", "corvette": "corvette_stealth"}[k]))
    except ImportError: pass
    try:
        import fleet_big as Bg
        reg["lpd"] = (Bg.lpd, Bg.lpd_anims); reg["sub"] = (Bg.sub, Bg.sub_anims); reg["airlifter"] = (Bg.airlifter, Bg.airlifter_anims)
    except ImportError: pass
    return reg


def self_test(meta, bones):
    """Tailgate / door swing must open the right way: free edge ends up beyond the hinge, level with the deck."""
    for n, piv, pt, rot, ax, sg, dmin in meta.get("swings", []):   # free edge must swing out the right way
        p = about(pt, piv, rot)
        assert sg * (p[ax] - piv[ax]) > dmin, (n, p)


def build(key, reg, preview):
    fn, anim_fn = reg[key]
    bones, meta = fn()
    lamps = L.add_lamps(bones, meta)
    bones = O.assign_uv(bones)
    anims = anim_fn()
    cubes = check(bones, anims)
    self_test(meta, bones)
    vid = meta["id"]
    tex = paint(meta["hull_rgb"], meta["belly_rgb"], **PAINT[vid])
    ext = extents(bones)
    if preview:
        os.makedirs(preview, exist_ok=True)
        pose = rest_pose(bones)
        kw = dict(W=760, H=420, scale=meta.get("scale", 1.6))
        v = meta.get('view', (35, -18))
        img = render(bones, tex, pose, v[0], v[1], **kw) + render(bones, tex, pose, v[0] + 180, v[1] + 3, **kw)
        save_png(os.path.join(preview, vid + ".png"), img)
    out = copy.deepcopy(bones)
    scale_uv(out)
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{"description": {
        "identifier": "geometry." + vid, "texture_width": ATLAS * 2, "texture_height": ATLAS * 2,
        "visible_bounds_width": meta.get("bounds_w", 12), "visible_bounds_height": meta.get("bounds_h", 6),
        "visible_bounds_offset": meta.get("bounds_off", [0, 1.5, 0])}, "bones": out}]}
    for sub in ("geo", "animations", "textures/entity"): os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    with open(os.path.join(OUT, "geo", vid + ".geo.json"), "w") as f: json.dump(geo, f, indent=1)
    with open(os.path.join(OUT, "animations", vid + ".animation.json"), "w") as f: json.dump(anims, f, indent=1)
    save_png(os.path.join(OUT, "textures", "entity", vid + ".png"), upscale2(tex))
    save_png(os.path.join(OUT, "textures", "entity", vid + "_glowmask.png"), glowmask2(tex))
    os.makedirs(os.path.join(DATA, "vehicle_lights"), exist_ok=True)
    with open(os.path.join(DATA, "vehicle_lights", vid + ".json"), "w") as f: json.dump({"unit": "px", "px_per_block": 16, "level": 13, "lamps": [list(l) for l in lamps]}, f)
    base = os.path.join(OUT, "textures", "entity", vid)
    for tag, (h, b) in meta.get("variants", {"thai": ((58, 74, 46), (40, 50, 34)), "desert": ((178, 152, 108), (120, 100, 70))}).items():
        save_png(f"{base}_{tag}.png", upscale2(paint(h, b, **PAINT[vid])))      # same UVs, different livery
        shutil.copyfile(base + "_glowmask.png", f"{base}_{tag}_glowmask.png")   # AutoGlowingGeoLayer looks up <texture>_glowmask.png
    print(f"{vid}: lamps={len(lamps)} cubes={cubes} bones={len(bones)} extents(px)={ext}")
    meta = dict(meta, _clips=[k.split('.', 2)[2] for k in anims['animations']])
    return meta, ext


def specs(rows):
    L = ["# Vehicle Fleet - collider and seat anchors", "",
         "Model space: nose -Z, +X vehicle left, +Y up, **16 px = 1 block**, ground y=0. Values are px; blocks = px / 16.", "",
         "Atlas: `textures/entity/<id>.png` is **1024x1024** = 16x16 cells of 64 px (UVs are written for 1024; the painter works on 512 and doubles).",
         "Every cube face maps one texel per model px (2 texels/px in the export) into the cell of its material, so repainting a cell repaints every part using it.", "",
         "| cell | material | use |", "|---|---|---|",
         "| 0 | HULL | weathered military paint (tinted per vehicle), rust drips, chipped edges |",
         "| 1 | BELLY | lower hull / anti-fouling / underbody, heavier grime |",
         "| 2 | GLASS | alpha-0 glazing with streaks (needs translucent render type) |",
         "| 3 | DARK | frames, chassis, hydraulics, greebles |", "| 4 / 18 | BLADE / TIP | rotor blades / yellow tip band |",
         "| 5 | WALK | non-skid deck grit with rust bloom |", "| 6 | TIRE | tyre rubber |", "| 7 | SPIN | bare steel, chrome oleo, cables |",
         "| 9 | SOOT | exhaust staining | ", "| 10 | GRILLE | radiator / intake grille |", "| 11 / 12 / 17 | RED / GREEN / WHITE | lamps, binders, markings |",
         "| 13 | WINDOW | opaque lit windows (ship superstructure) |", "| 14 | INTER | interior panels and seats |",
         "| 15 | RAMP | **diamond tread plate** (bed liners, ramps) |", "| 16 | DOOR | doors and hatches, same tint as HULL |", ""]
    for meta, ext in rows:
        L += [f"## {meta['name']} (`{meta['id']}`) - Tier {meta['tier']}", f"Payload: **{meta['payload']}**", f"Player seat capacity: **{meta.get('seat_capacity', '?')}**", "",
              f"Liveries: `{meta['id']}.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`", "", f"Model extents px: x {ext[0]}, y {ext[1]}, z {ext[2]}", "", "Walkable deck colliders (walking surface; box min / max, px -> blocks):", ""]
        for n, (a, b) in meta["decks"].items():
            L.append(f"- `{n}`: {a} -> {b}  =  {[round(v / 16, 2) for v in a]} -> {[round(v / 16, 2) for v in b]} "
                     f"(size {[round((b[i] - a[i]) / 16, 2) for i in range(3)]} blocks, give the slab ~0.25 block thickness under the surface)")
        if "interior" in meta:
            L += ["", "Walkable interior:", ""] + [f"- {line}" for line in meta["interior"]]
        if "mounts" in meta:
            L += ["", "Gun hard-points (`mount_*` bones; `pos` = gun pivot in px, facing deg: 0 = bow, +90 = left/+X; arc = traverse; pitch = elevation limits):", ""]
            for m in meta["mounts"]: L.append(f"- `{m['bone']}` pos {m['pos']} ({[round(v / 16, 2) for v in m['pos']]} blocks), {m['class']}, facing {m['facing']}, arc {m['arc']}, pitch {m['pitch']}")
        L += ["", "Seat / slot anchors (px):", ""]
        for n, p in meta["seats"].items(): L.append(f"- `{n}`: {p}")
        for k in ("extra",):
            for line in meta.get(k, []): L.append(f"- {line}")
        L.append("")
    return "\n".join(L)


KIND = {"technical_4x4": "ground", "ural_6x6": "ground", "recovery_6x6": "ground", "humvee_m1165": "ground",
        "mi17_hip": "air", "mi26_halo": "air", "uh60_blackhawk": "air", "c17_airlifter": "air"}   # everything else floats
DRAFT = {"fac_patrol": 18, "opv_cutter": 18, "corvette_stealth": 18, "lpd_assault": 22, "coaster_freighter": 24, "transport_sub": 60}
NOT_SEAT = ("titan", "exo", "hang", "sling", "stand", "bunk", "winch", "crane", "troop", "zone", "envelope")


def vehicle_spec(meta, ext):
    """Everything the Java side needs about a vehicle, in model px (+X left, nose -Z)."""
    clips = meta["_clips"]; pick = lambda names: next((n for n in names if n in clips), None)
    seats = [{"name": n, "pos": p} for n, p in meta.get("seats", {}).items() if isinstance(p, list) and len(p) == 3 and not any(w in n for w in NOT_SEAT)][:6]
    cargo = [{"name": n, "pos": p, "type": "titan" if "titan" in n else "exo"} for n, p in meta.get("seats", {}).items()
             if isinstance(p, list) and len(p) == 3 and ("titan" in n or "exo" in n) and "zone" not in n and "envelope" not in n]
    kind = KIND.get(meta["id"], "ship")
    return {"id": meta["id"], "name": meta["name"], "tier": meta["tier"], "kind": kind, "payload": meta["payload"], "seat_capacity": meta.get("seat_capacity", len(seats)),
            "seats": seats, "cargo": cargo, "half_width": max(abs(ext[0][0]), abs(ext[0][1])), "length": [ext[2][0], ext[2][1]], "height": ext[1][1], "draft": DRAFT.get(meta["id"], 0),
            "rgb": list(meta["hull_rgb"]), "clips": {"idle": pick(["idle"]), "move": pick(["fly", "drive", "taxi", "swim"]), "open": pick(["cargo_open", "ramp_open", "deck_open", "tailgate_open", "gate_open"]),
                                                      "sling": pick(["sling"]), "beacon": pick(["beacon"]), "radar": pick(["radar_spin"])},
            "speed": {"ground": 0.34 - 0.03 * (meta["tier"] - 1), "air": 0.9 - 0.15 * (meta["tier"] - 1), "ship": 0.42 - 0.09 * (meta["tier"] - 1)}[kind]}


def write_mod_data(rows):
    specs = [vehicle_spec(m, e) for m, e in rows]
    with open(os.path.join(DATA, "vehicles.json"), "w") as f: json.dump(specs, f, indent=1)
    lang = {"itemGroup.vehiclefleet": "Vehicle Fleet", "message.vehiclefleet.seat": "Seat %s / %s", "message.vehiclefleet.lights_on": "Lights on", "message.vehiclefleet.lights_off": "Lights off",
            "message.vehiclefleet.variant": "Livery: %s", "message.vehiclefleet.no_seat": "No free seat", "key.categories.vehiclefleet": "Vehicle Fleet", "key.vehiclefleet.seat": "Next seat",
            "key.vehiclefleet.climb": "Climb", "key.vehiclefleet.descend": "Descend", "key.vehiclefleet.open": "Open / close ramp, doors", "key.vehiclefleet.lights": "Toggle lights", "key.vehiclefleet.release": "Release cargo"}
    for sp in specs:
        lang[f"item.vehiclefleet.{sp['id']}"] = sp["name"]; lang[f"entity.vehiclefleet.{sp['id']}"] = sp["name"]
        with open(os.path.join(OUT, "models", "item", sp["id"] + ".json"), "w") as f: json.dump({"parent": "item/generated", "textures": {"layer0": f"vehiclefleet:item/{sp['id']}"}}, f)
        r, g, b = sp["rgb"]; px = [[(0, 0, 0, 0)] * 16 for _ in range(16)]                       # 16x16 icon: hull colour block with a dark outline and a roof stripe
        for y in range(3, 13):
            for x in range(1, 15):
                edge = y in (3, 12) or x in (1, 14); px[y][x] = (40, 42, 46, 255) if edge else (min(255, r + 25 * (y == 6)), min(255, g + 25 * (y == 6)), min(255, b + 25 * (y == 6)), 255)
        save_png(os.path.join(OUT, "textures", "item", sp["id"] + ".png"), px)
    with open(os.path.join(OUT, "lang", "en_us.json"), "w") as f: json.dump(lang, f, indent=1)


def main():
    reg = registry()
    keys = [a for a in sys.argv[1:] if a in reg] or list(reg)
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    rows = [build(k, reg, preview) for k in keys]
    if len(keys) == len(reg):
        for sub in ('models/item', 'textures/item', 'lang'): os.makedirs(os.path.join(OUT, sub), exist_ok=True)
        write_mod_data(rows)
    if len(keys) == len(reg):
        os.makedirs(os.path.join(HERE, "..", "docs"), exist_ok=True)
        with open(os.path.join(HERE, "..", "docs", "SPECS.md"), "w") as f: f.write(specs(rows))


if __name__ == "__main__":
    main()
