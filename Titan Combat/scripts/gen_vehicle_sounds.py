"""Synthesises seamless engine loops for transport vehicles (pure stdlib + ffmpeg for OGG).
Run from project root: python3 scripts/gen_vehicle_sounds.py"""
import math, random, struct, subprocess, wave, os, tempfile

SR = 22050
OUT = "src/main/resources/assets/titancombat/sounds/vehicle"


def noise_filtered(n, cutoff, seed):
    """One-pole low-passed white noise."""
    rnd = random.Random(seed)
    a = math.exp(-2 * math.pi * cutoff / SR)
    y, out = 0.0, []
    for _ in range(n):
        y = a * y + (1 - a) * (rnd.random() * 2 - 1)
        out.append(y)
    peak = max(abs(v) for v in out) or 1
    return [v / peak for v in out]


def loopable(sig, fade):
    """Crossfade the tail into the head so the loop has no click."""
    n = len(sig) - fade
    out = sig[:n]
    for i in range(fade):
        t = i / fade
        out[i] = out[i] * t + sig[n + i] * (1 - t)
    return out


def write(name, sig):
    peak = max(abs(v) for v in sig) or 1
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    with wave.open(tmp, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(v / peak * 0.9 * 32767)) for v in sig))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-c:a", "libvorbis", "-q:a", "5",
                    f"{OUT}/{name}.ogg"], check=True)
    os.remove(tmp)


def rotor(seconds, blade_hz, whine_hz, seed, slap=1.0):
    """Blade-slap 'whop' pulses at blade-pass frequency over turbine whine and wash."""
    n = int(SR * seconds)
    wash = noise_filtered(n, 900, seed)
    thump = noise_filtered(n, 220, seed + 1)
    out = []
    for i in range(n):
        t = i / SR
        ph = (t * blade_hz) % 1.0
        env = math.exp(-ph * 9.0)                      # sharp attack, quick decay per blade pass
        body = thump[i] * env * 1.6 * slap + math.sin(2 * math.pi * blade_hz * 2 * t) * env * 0.5
        whine = 0.10 * math.sin(2 * math.pi * whine_hz * t) + 0.05 * math.sin(2 * math.pi * whine_hz * 2.01 * t)
        out.append(body + wash[i] * 0.35 + whine)
    return loopable(out, int(SR * 0.15))


def diesel(seconds, fire_hz, seed, rough=0.5):
    """Firing-pulse rumble with harmonics, turbo hiss and exhaust grit."""
    n = int(SR * seconds)
    grit = noise_filtered(n, 400, seed)
    hiss = noise_filtered(n, 3000, seed + 2)
    rnd = random.Random(seed)
    out, jitter = [], 0.0
    for i in range(n):
        t = i / SR
        if i % 512 == 0: jitter = (rnd.random() - 0.5) * 0.06
        ph = (t * fire_hz * (1 + jitter)) % 1.0
        pulse = math.exp(-ph * 6.0)
        tone = sum(math.sin(2 * math.pi * fire_hz * k * t) / k for k in (0.5, 1, 2, 3))
        out.append(tone * 0.35 + pulse * grit[i] * (0.9 + rough) + hiss[i] * 0.05)
    return loopable(out, int(SR * 0.15))


def ship(seconds, seed):
    """Slow diesel throb plus broadband bow wash with swell."""
    n = int(SR * seconds)
    base = diesel(seconds + 0.15, 9.0, seed, rough=0.2)
    wash = noise_filtered(n + int(SR * 0.15), 700, seed + 5)
    out = []
    for i in range(len(base)):
        t = i / SR
        swell = 0.6 + 0.4 * math.sin(2 * math.pi * t / seconds)
        out.append(base[i] * 0.8 + wash[i] * 0.7 * swell)
    return loopable(out, int(SR * 0.15))


write("rotor_tandem", rotor(4.0, 9.0, 1450, 11))          # CH-47 heavy twin-rotor chop
write("rotor_tiltrotor", rotor(4.0, 12.5, 1900, 21, 0.8))  # V-22 proprotor buzz-chop
write("rotor_drone", rotor(3.0, 38.0, 2600, 31, 0.4))      # sky-crane multirotor
write("engine_diesel_heavy", diesel(3.0, 26.0, 41))        # 8x8 hauler / APC / trailer
write("engine_diesel_light", diesel(3.0, 38.0, 51, 0.3))   # tactical truck
write("engine_ship", ship(5.0, 61))                        # barge / carrier
print(sorted(os.listdir(OUT)))
