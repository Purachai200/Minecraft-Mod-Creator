#!/usr/bin/env python3
"""
Synthesises seamless audio loops for Vehicle Fleet:
- Helicopters: heavy (Mi-17, Mi-26) and light tactical (UH-60)
- Jet Airlifter: C-17 quad turbofan
- Ground vehicles: heavy diesel (Ural, Recovery) and light diesel (Humvee, Technical)
- Maritime vessels: heavy marine diesel (Freighter, OPV, Corvette, LPD, Patrol)
- Submarine: submerged electric drive hum
- Horns: truck horn and ship foghorn
Uses pure Python stdlib + ffmpeg for OGG encoding.
"""
import math, random, struct, subprocess, wave, os, tempfile

SR = 22050
OUT = r"c:\Users\Purachai\Desktop\Minecraft Mode Creator\minecraft_mod_creator\Vehicle Fleet\src\main\resources\assets\vehiclefleet\sounds\vehicle"
os.makedirs(OUT, exist_ok=True)

def noise_filtered(n, cutoff, seed):
    rnd = random.Random(seed)
    a = math.exp(-2 * math.pi * cutoff / SR)
    y, out = 0.0, []
    for _ in range(n):
        y = a * y + (1 - a) * (rnd.random() * 2 - 1)
        out.append(y)
    peak = max(abs(v) for v in out) or 1
    return [v / peak for v in out]

def loopable(sig, fade):
    n = len(sig) - fade
    out = sig[:n]
    for i in range(fade):
        t = i / fade
        out[i] = out[i] * t + sig[n + i] * (1 - t)
    return out

def write_ogg(name, sig):
    peak = max(abs(v) for v in sig) or 1
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    with wave.open(tmp, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(v / peak * 0.9 * 32767)) for v in sig))
    out_file = os.path.join(OUT, f"{name}.ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-c:a", "libvorbis", "-q:a", "5", out_file], check=True)
    os.remove(tmp)
    print(f"Generated {out_file} ({os.path.getsize(out_file)} bytes)")

def rotor(seconds, blade_hz, whine_hz, seed, slap=1.2):
    n = int(SR * seconds)
    wash = noise_filtered(n, 950, seed)
    thump = noise_filtered(n, 200, seed + 1)
    out = []
    for i in range(n):
        t = i / SR
        ph = (t * blade_hz) % 1.0
        env = math.exp(-ph * 8.5)
        body = thump[i] * env * 1.7 * slap + math.sin(2 * math.pi * blade_hz * 2 * t) * env * 0.6
        whine = 0.12 * math.sin(2 * math.pi * whine_hz * t) + 0.06 * math.sin(2 * math.pi * whine_hz * 2.01 * t)
        out.append(body + wash[i] * 0.40 + whine)
    return loopable(out, int(SR * 0.15))

def diesel(seconds, fire_hz, seed, rough=0.5):
    n = int(SR * seconds)
    grit = noise_filtered(n, 420, seed)
    hiss = noise_filtered(n, 2800, seed + 2)
    rnd = random.Random(seed)
    out, jitter = [], 0.0
    for i in range(n):
        t = i / SR
        if i % 512 == 0: jitter = (rnd.random() - 0.5) * 0.06
        ph = (t * fire_hz * (1 + jitter)) % 1.0
        pulse = math.exp(-ph * 6.0)
        tone = sum(math.sin(2 * math.pi * fire_hz * k * t) / k for k in (0.5, 1, 2, 3))
        out.append(tone * 0.35 + pulse * grit[i] * (0.9 + rough) + hiss[i] * 0.06)
    return loopable(out, int(SR * 0.15))

def ship(seconds, seed):
    n = int(SR * seconds)
    base = diesel(seconds + 0.15, 8.5, seed, rough=0.2)
    wash = noise_filtered(n + int(SR * 0.15), 650, seed + 5)
    out = []
    for i in range(len(base)):
        t = i / SR
        swell = 0.6 + 0.4 * math.sin(2 * math.pi * t / seconds)
        out.append(base[i] * 0.85 + wash[i] * 0.7 * swell)
    return loopable(out, int(SR * 0.15))

def jet(seconds, seed):
    n = int(SR * seconds)
    roar = noise_filtered(n, 1200, seed)
    hiss = noise_filtered(n, 4500, seed + 1)
    out = []
    for i in range(n):
        t = i / SR
        whine1 = 0.15 * math.sin(2 * math.pi * 1850 * t)
        whine2 = 0.08 * math.sin(2 * math.pi * 3700 * t)
        out.append(roar[i] * 0.65 + hiss[i] * 0.45 + whine1 + whine2)
    return loopable(out, int(SR * 0.15))

def submarine(seconds, seed):
    n = int(SR * seconds)
    muffle = noise_filtered(n, 320, seed)
    out = []
    for i in range(n):
        t = i / SR
        hum = 0.35 * math.sin(2 * math.pi * 60 * t) + 0.15 * math.sin(2 * math.pi * 120 * t)
        cavit = 0.10 * math.sin(2 * math.pi * 14 * t)
        out.append(muffle[i] * 0.7 + hum + cavit)
    return loopable(out, int(SR * 0.15))

def horn_truck(seconds=1.2):
    n = int(SR * seconds)
    out = []
    for i in range(n):
        t = i / SR
        env = min(1.0, t / 0.04) * (1.0 if t < seconds - 0.08 else (seconds - t) / 0.08)
        # Dual air horns: 310 Hz and 370 Hz
        sound = math.sin(2 * math.pi * 310 * t) + 0.8 * math.sin(2 * math.pi * 370 * t)
        sound += 0.3 * math.sin(2 * math.pi * 620 * t) + 0.2 * math.sin(2 * math.pi * 740 * t)
        out.append(sound * env * 0.7)
    return out

def horn_ship(seconds=2.5):
    n = int(SR * seconds)
    out = []
    for i in range(n):
        t = i / SR
        env = min(1.0, t / 0.15) * (1.0 if t < seconds - 0.25 else (seconds - t) / 0.25)
        # Deep foghorn 130 Hz with subharmonics
        sound = math.sin(2 * math.pi * 130 * t) + 0.6 * math.sin(2 * math.pi * 260 * t) + 0.3 * math.sin(2 * math.pi * 390 * t)
        out.append(sound * env * 0.8)
    return out

def main():
    print("Synthesizing Vehicle Fleet audio...")
    write_ogg("rotor_helo_heavy", rotor(4.0, 9.5, 1420, 101, slap=1.4))     # Mi-17 & Mi-26
    write_ogg("rotor_helo_light", rotor(3.5, 13.5, 1850, 102, slap=1.1))    # UH-60 Blackhawk
    write_ogg("engine_jet_heavy", jet(4.0, 103))                             # C-17 Globemaster
    write_ogg("engine_diesel_light", diesel(3.0, 36.0, 104, rough=0.3))      # Technical 4x4, Humvee
    write_ogg("engine_diesel_heavy", diesel(3.2, 24.0, 105, rough=0.6))      # Ural 6x6, Recovery 6x6
    write_ogg("engine_ship", ship(5.0, 106))                                 # Ships (Freighter, OPV, etc.)
    write_ogg("engine_submarine", submarine(4.5, 107))                       # Submarine
    write_ogg("horn_truck", horn_truck(1.2))
    write_ogg("horn_ship", horn_ship(2.2))
    print("Done generating sounds!")

if __name__ == '__main__':
    main()
