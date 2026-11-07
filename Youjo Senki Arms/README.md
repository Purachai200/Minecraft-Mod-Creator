# Arcane Infantry (`youjoarms`)

A standalone Forge 1.20.1 mod add-on for **TACZ (Timeless and Classics Zero)** that introduces WWI/WWII-era firearms with **mage-infantry formula casting** (inspired by anime aerial mage combat): glowing magic circles at the muzzle, colored streak tracers, and spell-infused munitions.

---

## Features

### 1. Historical Firearms & Munitions (TACZ Gun Pack)
- **Karabiner 98k**: Bolt-action rifle chambered in 7.92×57mm Mauser (5-round stripper clip, high damage, warm yellow-white streak tracer).
- **Gewehr 98**: Long WWI variant service rifle.
- **Mauser C96**: Broomhandle semi-automatic pistol.
- **MP 18**: Early trench submachine gun.
- **Mauser 1918 T-Gewehr**: Massive 13.2mm anti-materiel rifle adapted for heavy long-range artillery formula bombardment.
- **New**: Colt M1911 (.45 ACP), Springfield M1903 (.30-06), Thompson M1928 (.45 ACP), Browning M1918 BAR (.30-06).
- **Ammo**: every gun now uses TACZ's own ammo (`tacz:308`, `762x54`, `50bmg`, `9mm`, `45acp`, `30_06`, `12g`, `40mm`), so any ammo from TACZ or other mods that supplies those types works. The old `youjoarms:*` ammo items remain but no gun uses them.
- **Munitions (legacy items)**:
  - `7.92×57mm Mauser` (Standard yellow tracer)
  - `7.92×57mm Elenium-Infused` (Cyan streak tracer, higher penetration)
  - `13.2mm TuF Heavy Cartridge` (Artillery / heavy ammo)

### 2. Mage Formula Casting System
- **Mana System**: Player capability with mana pool (default max 100 MP) and passive mana regeneration.
- **Mana & Formula HUD**: Displays above the hotbar when holding a firearm.
- **Formula Types**:
  - `NONE`: Standard kinetic ballistics.
  - `EXPLOSIVE`: Explodes on hit (mob damage; block damage toggleable in config).
  - `PIERCING`: Significant damage multiplier and enhanced headshot multiplier.
  - `ARTILLERY`: Cancels normal bullet and launches an arcing glowing artillery shell entity with a magic particle trail and massive AoE blast.
- **Magic Circle VFX**: Procedural glowing runic magic circle renders in front of the muzzle when charging formulas, scaled by charge progress and visible to all players.

---

## Keybinds

| Action | Default Key | Description |
|---|---|---|
| **Charge / Cast Formula** | `G` | Hold while aiming/holding gun to charge the magic formula; fire while charged to consume mana and apply formula. |
| **Cycle Formula** | `V` | Cycles through available formulas: `NONE` -> `EXPLOSIVE` -> `PIERCING` -> `ARTILLERY`. |

---

## Assets & Status
- **Guns & Animations**: Kar98k uses TACZ Bedrock model structure with bolt-action animations. Gewehr 98, C96, MP18, and T-Gewehr use functional placeholder definitions and data.
- **Sounds**: Utilizes TACZ base sound event references (`tacz:springfield1873/*` and Minecraft vanilla spell/explosion effects).
- **TACZ Version Tested**: `tacz-1.20.1-1.1.6-hotfix.jar` on Forge `47.4.10`.

---

## Configuration (`youjoarms-common.toml`)
- `mana.maxMana`: Maximum mana pool (default: 100).
- `mana.manaRegenPerSecond`: Passive mana regen rate per second (default: 5).
- `formulas.explosive.manaCost`, `radius`, `blockDamage`: Explosive formula settings.
- `formulas.piercing.manaCost`, `damageMultiplier`: Piercing formula settings.
- `formulas.artillery.manaCost`, `radius`, `blockDamage`: Artillery shell settings.
