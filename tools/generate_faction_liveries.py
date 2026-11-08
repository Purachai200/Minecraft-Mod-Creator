#!/usr/bin/env python3
"""
Generates 4 additional high-fidelity camo/faction liveries for all 14 vehicles:
- _arctic: Arctic / Winter Snow Patrol
- _blackops: Night Stealth / Tactical Black SWAT
- _un: UN Peacekeeper Blue / White
- _redstar: Rebel / Red Star Crimson

Total liveries per vehicle: 7 (Default, Thai, Desert, Arctic, Blackops, UN, Redstar)
"""
import sys, os, shutil
sys.path.insert(0, r'c:\Users\Purachai\Desktop\Minecraft Mode Creator\minecraft_mod_creator\Vehicle Fleet\scripts')
sys.path.insert(0, r'c:\Users\Purachai\Desktop\Minecraft Mode Creator\minecraft_mod_creator\Titan Combat\scripts')

import gen_fleet as F

VARIANTS = {
    "arctic":   ((208, 216, 224), (158, 168, 178)),
    "blackops": ((36, 38, 42),    (24, 25, 28)),
    "un":       ((72, 128, 185),  (215, 220, 225)),
    "redstar":  ((132, 42, 42),   (78, 28, 28))
}

def main():
    tex_dir = r"c:\Users\Purachai\Desktop\Minecraft Mode Creator\minecraft_mod_creator\Vehicle Fleet\src\main\resources\assets\vehiclefleet\textures\entity"
    reg = F.registry()

    for key, (fn, _) in reg.items():
        _, meta = fn()
        vid = meta['id']
        paint_cfg = F.PAINT.get(vid, {})
        base_glow = os.path.join(tex_dir, f"{vid}_glowmask.png")

        for tag, (hull_rgb, belly_rgb) in VARIANTS.items():
            tex = F.paint(hull_rgb, belly_rgb, **paint_cfg)
            out_png = os.path.join(tex_dir, f"{vid}_{tag}.png")
            out_glow = os.path.join(tex_dir, f"{vid}_{tag}_glowmask.png")
            F.save_png(out_png, F.upscale2(tex))
            if os.path.exists(base_glow):
                shutil.copyfile(base_glow, out_glow)
            print(f"Generated {vid}_{tag}.png")

    print(f"Successfully generated all faction liveries for {len(reg)} vehicles!")

if __name__ == '__main__':
    main()
