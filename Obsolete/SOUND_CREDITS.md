# Sound Asset Credits & Attribution

All audio assets in `assets/obsolete/sounds/` are original sound effects procedurally synthesized via physical-modeling digital signal processing (DSP) algorithms implemented in `tools/synthesize_mod_sounds.py`.

No copyrighted materials, game sound rips, or audio samples from anime/commercial sources (including project-obsolete.com or the OBSOLETE anime) were used. All audio is dedicated to the public domain under **Creative Commons 0 (CC0 1.0 Universal / Public Domain Dedication)**.

---

## Synthesis Engine
- **Tool**: `Obsolete/tools/synthesize_mod_sounds.py`
- **Techniques**:
  - Swept-frequency sine oscillators for pneumatic and hydraulic piston motion
  - Second-order resonant biquad bandpass/lowpass/highpass filtering for metallic acoustic resonances
  - Exponential decay envelopes and non-linear polynomial saturation distortion for mechanical impact clatter
  - Filtered pink noise bursts for rocket exhaust, muzzle blast, and pneumatic vents
  - High-frequency ring modulation for ricochet whine and electrical stun arc discharge
- **Output Format**: Ogg Vorbis, 44.1 kHz, 16-bit mono

---

## Audio Asset Manifest & License

| Filename | Description / Physical Model | License | Author / Generator |
|---|---|---|---|
| `exoframe_step_walk_1.ogg` .. `4.ogg` | Hydraulic piston release, 48Hz sub-bass frame thud, titanium footplate clink | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_step_sprint_1.ogg` .. `4.ogg` | High-force sprint foot impact, boosted transient mechanical rattle and pneumatic hiss | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_servo_1.ogg` .. `3.ogg` | High-torque electric actuator whine, resonant biquad bandpass modulation | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_engine_idle.ogg` | 55Hz sub-harmonic turbine and auxiliary power unit (APU) idle hum loop | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_land.ogg` | Heavy suspension compression thump, dual hydraulic damper hiss | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_land_heavy.ogg` | Massive kinetic impact shockwave, chassis stress creak, full suspension bottoming | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_cockpit_open.ogg` | Pneumatic seal release hiss, motorized canopy slide, latch unlock | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_cockpit_close.ogg` | Canopy latch alignment clank, motorized slide, heavy pneumatic airtight seal lock | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_pilot_mount.ogg` | Pilot harness clamp, avionics boot-up frequency chirp, power relay engage | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_pilot_dismount.ogg` | Pilot harness release clunk, avionics power-down sweep | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `exoframe_alarm_low_hull.ogg` | Cockpit emergency hull breach warning chime (dual-tone 880Hz / 660Hz sequence) | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_rifle_fire_1.ogg` .. `3.ogg` | Heavy 12.7mm rifle muzzle crack, supersonic shockwave, breech mechanism cycle | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_sniper_fire.ogg` | 20mm anti-material cannon blast, extended resonant bass punch, barrel ringing | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_autocannon_fire_1.ogg` .. `3.ogg` | Rapid 25mm high-explosive autocannon thud, mechanized feeder click | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_minigun_spinup.ogg` | Rotary barrel cluster acceleration whine (120Hz -> 820Hz sweep) | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_minigun_fire_loop.ogg` | Continuous rotary cyclic fire (50 rounds/sec acoustic pulse cascade) | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_minigun_spindown.ogg` | Rotary barrel deceleration whine with friction damping (820Hz -> 80Hz sweep) | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_shotgun_fire.ogg` | Combat shotgun punch, wide acoustic spread burst, heavy pump rack | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_grenade_thump.ogg` | Low-pressure pneumatic grenade launcher barrel pop and projectile release | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_rocket_launch.ogg` | Solid-fuel rocket ignition crackle, sustained booster burn, nozzle roar | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_recoilless_fire.ogg` | Massive counter-mass vent roar, chamber percussion, high-impulse launch | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_flamethrower_fire.ogg` | Pressurized liquid propellant hiss, ignition pop, sustained turbulent flame rush | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_melee_swing.ogg` | Heavy mecha hydraulic arm swing whoosh and servo acceleration | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_melee_impact.ogg` | High-energy kinetic metal-on-metal collision, structural deformation crunch | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_stun_zap.ogg` | High-voltage capacitor bank discharge, electrical arc crackle and ring | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_empty_click.ogg` | Dry-fire firing pin strike on empty chamber | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_reload.ogg` | Heavy magazine eject, fresh magazine guide lock, charging handle rack | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
| `weapon_impact_metal_1.ogg` .. `3.ogg` | Bullet ricochet harmonic whine, armor plate spall and spark crackle | CC0 1.0 | Procedural Generator (`synthesize_mod_sounds.py`) |
