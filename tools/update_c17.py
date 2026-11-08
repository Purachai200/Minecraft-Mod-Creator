import os

p = r'c:\Users\Purachai\Desktop\Minecraft Mode Creator\minecraft_mod_creator\Vehicle Fleet\scripts\fleet_big.py'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

target = """    zs = [-190 + 20 * i for i in range(23)]
    for z0, z1 in zip(zs, zs[1:]): X(H.shell(z0, z1, HW, YB, TOP, w=4, floor=True, inner=INTER, roof=True))
    # upswept tail cone above the ramp
    zt = [270, 287, 304, 321, 338]
    for i, (z0, z1) in enumerate(zip(zt, zt[1:])):
        X(H.solid(z0, z1, 44 - 9 * (i + 1), 100 + 6 * i, 118 + 5 * i, c=4))"""

rep = """    zs = [-190 + 20 * i for i in range(24)]
    for z0, z1 in zip(zs, zs[1:]): X(H.shell(z0, z1, HW, YB, TOP, w=4, floor=True, inner=INTER, roof=True))
    # upswept tail cone above and behind the ramp
    zt = [270, 287, 304, 321, 338]
    for i, (z0, z1) in enumerate(zip(zt, zt[1:])):
        X(H.solid(z0, z1, 44 - 9 * (i + 1), 100 + 6 * i, 118 + 5 * i, c=4))
    for i, (z0, z1) in enumerate(zip(zt[:3], zt[1:4])):
        X(H.solid(z0, z1, 38 - 10 * (i + 1), 40 + 18 * i, 100 + 6 * i, c=3))"""

target2 = '"scale": 0.5, "bounds_w": 30, "bounds_h": 20, "bounds_off": [0, 8, 0]'
rep2 = '"scale": 0.5, "bounds_w": 52, "bounds_h": 28, "bounds_off": [0, 10, 0]'

assert target in text.replace('\r\n', '\n'), "target not found"
text = text.replace('\r\n', '\n').replace(target, rep).replace(target2, rep2)

with open(p, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(text)

print("fleet_big.py successfully updated!")
