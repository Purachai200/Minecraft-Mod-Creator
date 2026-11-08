#!/usr/bin/env python3
"""Battlefield / CoD Vehicle Seating & Cargo HUD Mockup Generator
Creates a visual preview image demonstrating the in-game bottom-left Tactical Vehicle Seat Indicator:
- Vehicle 2D wireframe silhouette (Tactical Technical 4x4)
- Seat 1 (Driver ✇) - Occupied by Current Player (Gold/Yellow)
- Seat 2 (Passenger) - Occupied by Teammate (Cyan/Green)
- Seat 3 & 4 (Bed Gunners) - Walkable Deck standing zones
- Cargo Bay Status - Obsolete Exoframe Docked & Charging (95% FE)
Output: vehicle_seat_hud_preview.png
"""

import math
import os
import struct
import zlib
from PIL import Image, ImageDraw, ImageFont

def make_hud_preview():
    # Simulated Minecraft Screen (1280 x 720) with a dark translucent HUD widget at bottom-left
    W, H = 960, 540
    img = Image.new("RGBA", (W, H), (18, 22, 28, 255))
    draw = ImageDraw.Draw(img)

    # Simulated in-game background (subtle gradient grid)
    for y in range(0, H, 20):
        draw.line([(0, y), (W, y)], fill=(24, 30, 38, 255), width=1)
    for x in range(0, W, 20):
        draw.line([(x, 0), (x, H)], fill=(24, 30, 38, 255), width=1)

    # HUD Box Position: Bottom-Left (x: 24, y: H - 210)
    bx, by, bw, bh = 28, H - 220, 340, 190

    # Slate military HUD background (rounded rectangle with high-tech cyan/green accents)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(10, 14, 18, 230), outline=(0, 220, 255, 180), width=1)
    draw.line([(bx + 12, by + 28), (bx + bw - 12, by + 28)], fill=(0, 180, 220, 100), width=1)

    # Header Text
    draw.text((bx + 14, by + 8), "VEHICLE STATUS // TACTICAL TECHNICAL 4x4", fill=(0, 230, 255, 255))
    draw.text((bx + bw - 68, by + 8), "[TIER 1]", fill=(255, 190, 40, 255))

    # Top-Down Vehicle Schematic Wireframe (Left side of widget: x: bx + 16, y: by + 36, w: 90, h: 140)
    vx, vy = bx + 24, by + 40
    # Hood & Cab outline
    draw.rectangle([vx + 14, vy, vx + 66, vy + 40], outline=(70, 90, 110, 255), width=2) # Hood
    draw.rectangle([vx + 10, vy + 40, vx + 70, vy + 85], outline=(0, 220, 255, 255), width=2) # Cab
    draw.rectangle([vx + 12, vy + 85, vx + 68, vy + 135], outline=(120, 140, 160, 255), width=2) # Cargo Bed
    # 4 Wheels
    wheel_col = (45, 55, 65, 255)
    draw.rectangle([vx, vy + 12, vx + 10, vy + 38], fill=wheel_col, outline=(0, 220, 255, 200), width=1) # FL
    draw.rectangle([vx + 70, vy + 12, vx + 80, vy + 38], fill=wheel_col, outline=(0, 220, 255, 200), width=1) # FR
    draw.rectangle([vx, vy + 98, vx + 10, vy + 124], fill=wheel_col, outline=(0, 220, 255, 200), width=1) # RL
    draw.rectangle([vx + 70, vy + 98, vx + 80, vy + 124], fill=wheel_col, outline=(0, 220, 255, 200), width=1) # RR

    # Inside Schematic: Seat Dots
    # Seat 1: Driver (Yellow - Current Player)
    draw.ellipse([vx + 18, vy + 50, vx + 34, vy + 66], fill=(255, 200, 0, 255), outline=(255, 255, 255, 255), width=1)
    draw.text((vx + 23, vy + 52), "1", fill=(0, 0, 0, 255))

    # Seat 2: Passenger (Cyan - Teammate)
    draw.ellipse([vx + 46, vy + 50, vx + 62, vy + 66], fill=(0, 220, 180, 255), outline=(255, 255, 255, 255), width=1)
    draw.text((vx + 51, vy + 52), "2", fill=(0, 0, 0, 255))

    # Bed Deck Gunner Standing Zones (Dotted Circles)
    draw.ellipse([vx + 20, vy + 98, vx + 34, vy + 112], outline=(0, 220, 255, 180), width=1) # Left Gunner
    draw.text((vx + 24, vy + 100), "3", fill=(0, 220, 255, 255))
    draw.ellipse([vx + 46, vy + 98, vx + 60, vy + 112], outline=(0, 220, 255, 180), width=1) # Right Gunner
    draw.text((vx + 50, vy + 100), "4", fill=(0, 220, 255, 255))

    # Cargo Clamp Icon (Center of bed)
    draw.rectangle([vx + 32, vy + 100, vx + 48, vy + 126], fill=(255, 140, 20, 220), outline=(255, 255, 255, 255), width=1)
    draw.text((vx + 35, vy + 106), "EXO", fill=(0, 0, 0, 255))

    # Right Side: Seat Roster & Status Details (x: bx + 125)
    rx = bx + 124
    ry = by + 36

    # Seat 1 Detail
    draw.text((rx, ry), "[F1] ✇ PILOT:", fill=(255, 200, 0, 255))
    draw.text((rx + 72, ry), "YOU (Driving)", fill=(255, 255, 255, 255))

    # Seat 2 Detail
    draw.text((rx, ry + 22), "[F2] 👤 CO-PILOT:", fill=(0, 220, 180, 255))
    draw.text((rx + 82, ry + 22), "Alex_Gunner", fill=(200, 220, 240, 255))

    # Seat 3 & 4 (Bed Standing Gunner Slots)
    draw.text((rx, ry + 44), "[F3/F4] 🎯 BED DECK:", fill=(140, 160, 180, 255))
    draw.text((rx + 98, ry + 44), "2 STANDING SLOTS", fill=(100, 200, 100, 255))

    # Cargo Clamping Status Box
    draw.rounded_rectangle([rx, ry + 70, rx + 200, ry + 138], radius=4, fill=(18, 24, 32, 240), outline=(255, 140, 20, 180), width=1)
    draw.text((rx + 8, ry + 75), "CARGO DOCK // TIER 1 CLAMP", fill=(255, 160, 30, 255))
    draw.text((rx + 8, ry + 93), "• UNIT: Obsolete Exoframe (Locked)", fill=(220, 230, 240, 255))
    draw.text((rx + 8, ry + 109), "• STATUS: Auto-Repairing (100% HP)", fill=(100, 255, 120, 255))
    draw.text((rx + 8, ry + 123), "• POWER: Inductive Charge +50 FE/s", fill=(0, 220, 255, 255))

    brain_dir = os.path.abspath("C:/Users/Purachai/.gemini/antigravity/brain/d0082229-568a-4374-9437-f2414c618d6a")
    out_path = os.path.join(brain_dir, "vehicle_seat_hud_preview.png")
    img.save(out_path)
    print("SUCCESS: Battlefield Seat HUD Mockup rendered to:", out_path)

if __name__ == "__main__":
    make_hud_preview()
