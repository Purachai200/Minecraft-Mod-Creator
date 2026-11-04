"""
Procedural Physical-Modeling Sound Generator for OBSOLETE Mecha Mod.
Synthesizes 100% original, CC0-licensed audio files using physical modeling algorithms
(swept-frequency sine oscillators, metallic biquad bandpass resonators,
exponential decay envelopes, turbulent pink noise, and saturation distortion).
Converts to Vorbis .ogg via ffmpeg.
"""
import wave
import struct
import math
import random
import os
import subprocess

SAMPLE_RATE = 44100
OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src/main/resources/assets/obsolete/sounds"))
SCRATCH_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "scratch/audio_temp"))

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(SCRATCH_DIR, exist_ok=True)

# ----------------- DSP UTILITIES -----------------

def clamp(val, low=-1.0, high=1.0):
    return max(low, min(high, val))

def biquad_filter(samples, ftype, cutoff, q=1.0):
    w0 = 2 * math.pi * cutoff / SAMPLE_RATE
    alpha = math.sin(w0) / (2 * q)
    cos_w0 = math.cos(w0)

    if ftype == "lp":
        b0 = (1 - cos_w0) / 2
        b1 = 1 - cos_w0
        b2 = (1 - cos_w0) / 2
        a0 = 1 + alpha
        a1 = -2 * cos_w0
        a2 = 1 - alpha
    elif ftype == "hp":
        b0 = (1 + cos_w0) / 2
        b1 = -(1 + cos_w0)
        b2 = (1 + cos_w0) / 2
        a0 = 1 + alpha
        a1 = -2 * cos_w0
        a2 = 1 - alpha
    elif ftype == "bp":
        b0 = alpha
        b1 = 0
        b2 = -alpha
        a0 = 1 + alpha
        a1 = -2 * cos_w0
        a2 = 1 - alpha
    else:
        return samples

    out = []
    x1 = x2 = y1 = y2 = 0.0
    for x in samples:
        y = (b0/a0)*x + (b1/a0)*x1 + (b2/a0)*x2 - (a1/a0)*y1 - (a2/a0)*y2
        x2, x1 = x1, x
        y2, y1 = y1, y
        out.append(y)
    return out

def export_wav(filename, samples):
    wav_path = os.path.join(SCRATCH_DIR, filename + ".wav")
    ogg_path = os.path.join(OUT_DIR, filename + ".ogg")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        packed = bytearray()
        for s in samples:
            val = int(clamp(s, -0.99, 0.99) * 32767)
            packed.extend(struct.pack("<h", val))
        wf.writeframes(bytes(packed))

    # Convert to vorbis ogg
    cmd = ["/opt/homebrew/bin/ffmpeg", "-y", "-i", wav_path, "-c:a", "libvorbis", "-q:a", "4", ogg_path]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ogg_path

# ----------------- SOUND SYNTHESIS FUNCTIONS -----------------

def gen_step_walk(var_id):
    # Heavy hydraulic footstep: sub-bass kick + metal ring + pneumatic release
    dur = 0.42
    n = int(SAMPLE_RATE * dur)
    f_sub = 65.0 + var_id * 5.0
    f_ring1 = 380.0 + var_id * 25.0
    f_ring2 = 820.0 + var_id * 35.0
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Sub-bass transient
        p = f_sub * math.exp(-t * 22.0) + 28.0
        sub = math.sin(2 * math.pi * p * t) * math.exp(-t * 14.0)
        # Metal plate strike
        clank = (math.sin(2 * math.pi * f_ring1 * t) * 0.55 + math.sin(2 * math.pi * f_ring2 * t) * 0.35) * math.exp(-t * 26.0)
        # Hydraulic hiss burst
        hiss = (random.random() * 2.0 - 1.0) * math.exp(-max(0.0, t - 0.04) * 16.0) if t > 0.02 else 0.0
        sample = sub * 0.75 + clank * 0.45 + hiss * 0.28
        raw.append(sample)
    filtered = biquad_filter(raw, "lp", 3400, 1.0)
    export_wav(f"exoframe_step_walk_{var_id}", filtered)

def gen_step_sprint(var_id):
    # Sprint footstep: heavier kinetic slam + sharper pneumatic hiss
    dur = 0.36
    n = int(SAMPLE_RATE * dur)
    f_sub = 80.0 + var_id * 8.0
    f_ring = 460.0 + var_id * 40.0
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = f_sub * math.exp(-t * 28.0) + 32.0
        sub = math.sin(2 * math.pi * p * t) * math.exp(-t * 16.0)
        clank = (math.sin(2 * math.pi * f_ring * t) * 0.6 + math.sin(2 * math.pi * (f_ring * 2.1) * t) * 0.3) * math.exp(-t * 30.0)
        hiss = (random.random() * 2.0 - 1.0) * math.exp(-max(0.0, t - 0.03) * 20.0) if t > 0.015 else 0.0
        sample = sub * 0.85 + clank * 0.5 + hiss * 0.35
        raw.append(sample)
    filtered = biquad_filter(raw, "lp", 3800, 1.1)
    export_wav(f"exoframe_step_sprint_{var_id}", filtered)

def gen_servo(var_id):
    # Hydraulic servo/motor whine
    dur = 0.35
    n = int(SAMPLE_RATE * dur)
    base_f = 420.0 + var_id * 30.0
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / dur))  # smooth window
        f1 = base_f + 80.0 * math.sin(2 * math.pi * 12.0 * t)
        f2 = f1 * 2.0
        tone = math.sin(2 * math.pi * f1 * t) * 0.6 + math.sin(2 * math.pi * f2 * t) * 0.3
        hum = (random.random() * 2.0 - 1.0) * 0.15
        raw.append((tone + hum) * env * 0.6)
    export_wav(f"exoframe_servo_{var_id}", raw)

def gen_engine_idle():
    # Low-frequency diesel/turbine idle hum
    dur = 2.0
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # 55Hz + harmonics + low frequency rumble
        h1 = math.sin(2 * math.pi * 55.0 * t) * 0.5
        h2 = math.sin(2 * math.pi * 110.0 * t) * 0.3
        h3 = math.sin(2 * math.pi * 165.0 * t) * 0.15
        rumble = (random.random() * 2.0 - 1.0) * 0.12
        raw.append(h1 + h2 + h3 + rumble)
    filtered = biquad_filter(raw, "lp", 450, 0.8)
    export_wav("exoframe_engine_idle", filtered)

def gen_landing(heavy=False):
    # Massive shock-absorber landing thud
    dur = 0.65 if heavy else 0.45
    n = int(SAMPLE_RATE * dur)
    f0 = 90.0 if heavy else 75.0
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = f0 * math.exp(-t * 18.0) + 24.0
        sub = math.sin(2 * math.pi * p * t) * math.exp(-t * 9.0)
        clatter = (math.sin(2 * math.pi * 320.0 * t) * 0.5 + math.sin(2 * math.pi * 640.0 * t) * 0.3) * math.exp(-t * 18.0)
        hiss = (random.random() * 2.0 - 1.0) * math.exp(-t * 12.0)
        sample = sub * 0.9 + clatter * 0.5 + hiss * 0.4
        raw.append(sample)
    filtered = biquad_filter(raw, "lp", 2800 if heavy else 3200, 1.0)
    export_wav("exoframe_land_heavy" if heavy else "exoframe_land", filtered)

def gen_cockpit_hatch(open_hatch=True):
    # Hatch mechanism: metal latch clack + pneumatic hiss
    dur = 0.55
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        if open_hatch:
            # Click at start, hiss expanding
            click = math.sin(2 * math.pi * 1200.0 * t) * math.exp(-t * 80.0) if t < 0.05 else 0.0
            hiss = (random.random() * 2.0 - 1.0) * math.exp(-max(0.0, t - 0.05) * 8.0)
            sample = click * 0.6 + hiss * 0.35
        else:
            # Hiss first, heavy slam at end
            hiss = (random.random() * 2.0 - 1.0) * math.exp(-t * 10.0)
            slam_t = max(0.0, t - 0.28)
            slam = (math.sin(2 * math.pi * 120.0 * slam_t) + math.sin(2 * math.pi * 450.0 * slam_t) * 0.5) * math.exp(-slam_t * 25.0) if t >= 0.28 else 0.0
            sample = hiss * 0.25 + slam * 0.8
        raw.append(sample)
    export_wav("exoframe_cockpit_open" if open_hatch else "exoframe_cockpit_close", raw)

def gen_pilot_mount(mount=True):
    # Harness buckle + system power up/down
    dur = 0.6
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Buckle click
        click = math.sin(2 * math.pi * 1800.0 * t) * math.exp(-t * 90.0)
        # Electronic power up (sine pitch sweep up 200->600Hz) or power down (600->200Hz)
        if mount:
            sweep_f = 220.0 + 440.0 * min(1.0, t / 0.4)
            tone = math.sin(2 * math.pi * sweep_f * t) * 0.35 * min(1.0, t / 0.1) * math.exp(-max(0.0, t - 0.35) * 12.0)
        else:
            sweep_f = 660.0 - 440.0 * min(1.0, t / 0.4)
            tone = math.sin(2 * math.pi * sweep_f * t) * 0.35 * min(1.0, t / 0.1) * math.exp(-max(0.0, t - 0.35) * 12.0)
        raw.append(click * 0.5 + tone)
    export_wav("exoframe_pilot_mount" if mount else "exoframe_pilot_dismount", raw)

def gen_cockpit_alarm():
    # Cockpit low hull emergency warning beeps (dual-tone 880Hz / 1174Hz pulses)
    dur = 0.5
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        pulse1 = math.sin(2 * math.pi * 880.0 * t) * 0.4 if (0.05 < t < 0.20) else 0.0
        pulse2 = math.sin(2 * math.pi * 1174.0 * t) * 0.4 if (0.28 < t < 0.43) else 0.0
        raw.append(pulse1 + pulse2)
    export_wav("exoframe_alarm_low_hull", raw)

# ----------------- WEAPON SOUNDS -----------------

def gen_rifle_fire(var_id):
    # Heavy 20mm kinetic rifle crack + explosive expansion + breech clack
    dur = 0.48
    n = int(SAMPLE_RATE * dur)
    f_crack = 1200.0 + var_id * 80.0
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Supersonic shock crack (distorted impulse)
        crack = math.sin(2 * math.pi * f_crack * math.exp(-t * 40.0) * t) * math.exp(-t * 35.0)
        # Deep explosive pressure wave (80Hz down to 35Hz)
        boom = math.sin(2 * math.pi * (85.0 * math.exp(-t * 20.0) + 35.0) * t) * math.exp(-t * 10.0)
        # Muzzle blast white noise
        blast = (random.random() * 2.0 - 1.0) * math.exp(-t * 25.0)
        # Mechanical breech cycle clack at t=0.15
        clack_t = max(0.0, t - 0.14)
        clack = math.sin(2 * math.pi * 1400.0 * clack_t) * math.exp(-clack_t * 60.0) if t >= 0.14 else 0.0

        sample = crack * 0.7 + boom * 0.8 + blast * 0.45 + clack * 0.35
        # Soft saturation distortion for punch
        sample = math.tanh(sample * 1.6)
        raw.append(sample)
    filtered = biquad_filter(raw, "lp", 5500, 1.0)
    export_wav(f"weapon_rifle_fire_{var_id}", filtered)

def gen_sniper_fire():
    # Massive sabot anti-materiel cannon crack + long thunderous rumble
    dur = 0.95
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        crack = math.sin(2 * math.pi * 2200.0 * math.exp(-t * 50.0) * t) * math.exp(-t * 40.0)
        boom = math.sin(2 * math.pi * (110.0 * math.exp(-t * 15.0) + 25.0) * t) * math.exp(-t * 5.0)
        blast = (random.random() * 2.0 - 1.0) * math.exp(-t * 18.0)
        sample = math.tanh((crack * 0.85 + boom * 1.0 + blast * 0.5) * 1.8)
        raw.append(sample)
    filtered = biquad_filter(raw, "lp", 6200, 1.0)
    export_wav("weapon_sniper_fire", filtered)

def gen_autocannon_fire(var_id):
    # Heavy 30mm thumping automatic cannon
    dur = 0.4
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        crack = math.sin(2 * math.pi * 950.0 * t) * math.exp(-t * 45.0)
        boom = math.sin(2 * math.pi * (120.0 * math.exp(-t * 30.0) + 40.0) * t) * math.exp(-t * 12.0)
        blast = (random.random() * 2.0 - 1.0) * math.exp(-t * 30.0)
        sample = math.tanh((crack * 0.6 + boom * 0.9 + blast * 0.4) * 1.7)
        raw.append(sample)
    filtered = biquad_filter(raw, "lp", 4800, 1.0)
    export_wav(f"weapon_autocannon_fire_{var_id}", filtered)

def gen_minigun_sounds():
    # Spin-up (0.6s), loop (0.4s), spin-down (0.8s)
    # 1. Spin-up
    n = int(SAMPLE_RATE * 0.6)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        f = 150.0 + 750.0 * (t / 0.6)**2
        tone = math.sin(2 * math.pi * f * t) * 0.5 * (t / 0.6)
        hum = (random.random() * 2.0 - 1.0) * 0.15
        raw.append(tone + hum)
    export_wav("weapon_minigun_spinup", raw)

    # 2. Fire Loop (Rapid 3000 RPM bursts)
    n = int(SAMPLE_RATE * 0.4)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Multiple cyclic pops
        cycle = math.sin(2 * math.pi * 50.0 * t)  # 50 Hz = 3000 RPM
        pop = math.sin(2 * math.pi * 1400.0 * t) * (1.0 if cycle > 0.7 else 0.0) * 0.6
        boom = math.sin(2 * math.pi * 90.0 * t) * 0.4
        blast = (random.random() * 2.0 - 1.0) * 0.35
        raw.append(math.tanh(pop + boom + blast))
    export_wav("weapon_minigun_fire_loop", raw)

    # 3. Spin-down
    n = int(SAMPLE_RATE * 0.75)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        f = 900.0 * (1.0 - t / 0.75)**2 + 80.0
        tone = math.sin(2 * math.pi * f * t) * 0.45 * (1.0 - t / 0.75)
        raw.append(tone)
    export_wav("weapon_minigun_spindown", raw)

def gen_shotgun_fire():
    # Heavy 12GA breacher blast + pump sound
    dur = 0.55
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        boom = math.sin(2 * math.pi * 65.0 * t) * math.exp(-t * 12.0)
        blast = (random.random() * 2.0 - 1.0) * math.exp(-t * 20.0)
        sample = math.tanh((boom * 0.9 + blast * 0.7) * 1.9)
        raw.append(sample)
    filtered = biquad_filter(raw, "lp", 4200, 1.0)
    export_wav("weapon_shotgun_fire", filtered)

def gen_grenade_thump():
    # Pneumatic 40mm launcher thump + revolving cylinder click
    dur = 0.45
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        thump = math.sin(2 * math.pi * (140.0 * math.exp(-t * 30.0) + 45.0) * t) * math.exp(-t * 15.0)
        puff = (random.random() * 2.0 - 1.0) * math.exp(-t * 35.0)
        click_t = max(0.0, t - 0.2)
        click = math.sin(2 * math.pi * 1600.0 * click_t) * math.exp(-click_t * 70.0) if t >= 0.2 else 0.0
        sample = thump * 0.85 + puff * 0.4 + click * 0.35
        raw.append(sample)
    export_wav("weapon_grenade_thump", raw)

def gen_rocket_launch():
    # Rocket whoosh + high-pressure backblast
    dur = 0.85
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        ignition = math.sin(2 * math.pi * 110.0 * t) * math.exp(-t * 20.0)
        # Expanding rocket roar
        env = math.sin(math.pi * min(1.0, t / 0.5)) * math.exp(-max(0.0, t - 0.4) * 6.0)
        roar = (random.random() * 2.0 - 1.0) * env * 0.75
        sub = math.sin(2 * math.pi * 45.0 * t) * env * 0.4
        raw.append(ignition * 0.6 + roar + sub)
    filtered = biquad_filter(raw, "lp", 3600, 0.9)
    export_wav("weapon_rocket_launch", filtered)

def gen_recoilless_fire():
    # Recoilless rifle launch: massive shockwave crack and rear venturi roar
    dur = 0.7
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        crack = math.sin(2 * math.pi * 1800.0 * math.exp(-t * 40.0) * t) * math.exp(-t * 30.0)
        boom = math.sin(2 * math.pi * 50.0 * t) * math.exp(-t * 8.0)
        backblast = (random.random() * 2.0 - 1.0) * math.exp(-t * 16.0)
        sample = math.tanh((crack * 0.8 + boom * 0.9 + backblast * 0.6) * 1.8)
        raw.append(sample)
    filtered = biquad_filter(raw, "lp", 5000, 1.0)
    export_wav("weapon_recoilless_fire", filtered)

def gen_flamethrower_fire():
    # Roaring pressurized liquid fire jet
    dur = 0.6
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / dur))
        hiss = (random.random() * 2.0 - 1.0) * 0.6
        rumble = math.sin(2 * math.pi * 75.0 * t) * 0.3
        raw.append((hiss + rumble) * env)
    filtered = biquad_filter(raw, "lp", 2400, 1.2)
    export_wav("weapon_flamethrower_fire", filtered)

def gen_melee_swing():
    # Heavy servo blade whoosh
    dur = 0.35
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / dur))
        whoosh = (random.random() * 2.0 - 1.0) * env * 0.5
        motor = math.sin(2 * math.pi * (350.0 + 200.0 * (t / dur)) * t) * env * 0.35
        raw.append(whoosh + motor)
    filtered = biquad_filter(raw, "lp", 2200, 1.0)
    export_wav("weapon_melee_swing", filtered)

def gen_melee_impact():
    # Heavy metal crushing impact / blade cleave
    dur = 0.45
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        crush = (math.sin(2 * math.pi * 180.0 * t) + math.sin(2 * math.pi * 520.0 * t) * 0.5) * math.exp(-t * 22.0)
        crunch = (random.random() * 2.0 - 1.0) * math.exp(-t * 30.0) * 0.45
        raw.append(crush * 0.8 + crunch)
    export_wav("weapon_melee_impact", raw)

def gen_stun_zap():
    # High-voltage electrical arc discharge
    dur = 0.38
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        spark = (random.random() * 2.0 - 1.0) * math.exp(-t * 20.0)
        buzz = math.sin(2 * math.pi * 120.0 * t) * math.sin(2 * math.pi * 2400.0 * t) * math.exp(-t * 15.0)
        raw.append(spark * 0.6 + buzz * 0.5)
    export_wav("weapon_stun_zap", raw)

def gen_empty_click():
    # Dry firing pin click
    dur = 0.12
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        click = math.sin(2 * math.pi * 2600.0 * t) * math.exp(-t * 120.0)
        body = math.sin(2 * math.pi * 650.0 * t) * math.exp(-t * 80.0)
        raw.append(click * 0.6 + body * 0.3)
    export_wav("weapon_empty_click", raw)

def gen_reload():
    # Heavy magazine insert + bolt rack
    dur = 0.75
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Mag in at 0.12s
        t_mag = max(0.0, t - 0.12)
        mag = math.sin(2 * math.pi * 800.0 * t_mag) * math.exp(-t_mag * 50.0) if t >= 0.12 else 0.0
        # Bolt pull at 0.42s
        t_bolt = max(0.0, t - 0.42)
        bolt = (math.sin(2 * math.pi * 1800.0 * t_bolt) + math.sin(2 * math.pi * 420.0 * t_bolt) * 0.6) * math.exp(-t_bolt * 40.0) if t >= 0.42 else 0.0
        raw.append(mag * 0.6 + bolt * 0.7)
    export_wav("weapon_reload", raw)

def gen_impact_metal(var_id):
    # Ricochet & armor plate hit
    dur = 0.35
    n = int(SAMPLE_RATE * dur)
    f_whine = 2200.0 + var_id * 350.0
    f_clink = 850.0 + var_id * 120.0
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        whine = math.sin(2 * math.pi * (f_whine * math.exp(-t * 12.0)) * t) * math.exp(-t * 18.0)
        plate = math.sin(2 * math.pi * f_clink * t) * math.exp(-t * 30.0)
        spark = (random.random() * 2.0 - 1.0) * math.exp(-t * 40.0)
        raw.append(whine * 0.45 + plate * 0.55 + spark * 0.25)
    export_wav(f"weapon_impact_metal_{var_id}", raw)

# ----------------- MAIN EXECUTION -----------------

def gen_roller_dash():
    # Heel roller pods: rising electric motor whine over a gritty tyre/skid hiss (loops every 0.5 s)
    dur = 0.55
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        whine = math.sin(2 * math.pi * (820.0 + 260.0 * t) * t) * 0.28 + math.sin(2 * math.pi * 1640.0 * t) * 0.10
        grit = (random.random() * 2.0 - 1.0) * (0.35 + 0.25 * random.random())
        env = min(1.0, t / 0.03) * min(1.0, (dur - t) / 0.05)
        raw.append((whine + grit * 0.6) * env)
    hiss = biquad_filter(raw, "bp", 2400, 0.9)
    body = biquad_filter(raw, "lp", 1800, 0.7)
    export_wav("exoframe_roller_dash", [clamp(0.7 * a + 0.6 * b) for a, b in zip(hiss, body)])


def gen_hydro_jet():
    # Muffled underwater impeller: low pulsing thrum and churn, heavily low-passed
    dur = 1.0
    n = int(SAMPLE_RATE * dur)
    raw = []
    for i in range(n):
        t = i / SAMPLE_RATE
        thrum = math.sin(2 * math.pi * 72.0 * t) * (0.5 + 0.2 * math.sin(2 * math.pi * 9.0 * t))
        blade = math.sin(2 * math.pi * 216.0 * t) * 0.18
        churn = (random.random() * 2.0 - 1.0) * 0.4
        env = min(1.0, t / 0.05) * min(1.0, (dur - t) / 0.08)
        raw.append((thrum + blade + churn) * env)
    export_wav("exoframe_hydro_jet", biquad_filter(raw, "lp", 380, 0.8))


if __name__ == "__main__":
    print(f"Synthesizing all custom mecha sound effects into {OUT_DIR}...")
    for v in (1, 2, 3, 4):
        gen_step_walk(v)
        gen_step_sprint(v)
    for v in (1, 2, 3):
        gen_servo(v)
        gen_rifle_fire(v)
        gen_autocannon_fire(v)
        gen_impact_metal(v)

    gen_engine_idle()
    gen_roller_dash()
    gen_hydro_jet()
    gen_landing(heavy=False)
    gen_landing(heavy=True)
    gen_cockpit_hatch(open_hatch=True)
    gen_cockpit_hatch(open_hatch=False)
    gen_pilot_mount(mount=True)
    gen_pilot_mount(mount=False)
    gen_cockpit_alarm()

    gen_sniper_fire()
    gen_minigun_sounds()
    gen_shotgun_fire()
    gen_grenade_thump()
    gen_rocket_launch()
    gen_recoilless_fire()
    gen_flamethrower_fire()
    gen_melee_swing()
    gen_melee_impact()
    gen_stun_zap()
    gen_empty_click()
    gen_reload()

    print("All sound effects synthesized successfully!")
