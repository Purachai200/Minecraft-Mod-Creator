# Agent Prompt: Youjo Senki Arms — TACZ add-on (new standalone mod)

## Goal
Create a **new, separate Forge mod** that adds WWI/WWII-era bolt-action and early-automatic rifles to **TACZ (Timeless and Classics Zero)**, with **mage-infantry "formula" casting**: a magic circle appears at the muzzle while charging, the shot fires with a **colored streak tracer**, and special formulas (explosive, piercing, artillery) cost mana.

Visual reference: mage infantry in a 1920s-style alternate-history war anime — rifles with bayonets, glowing magic circles in front of the barrel, bright colored streak bullets, explosive "artillery formula" shots fired from the air.

Do NOT copy anime logos, character art or names into assets or the mod page. The guns themselves are real historical firearms and are fine to use.

## Hard constraints
- **Minecraft 1.20.1, Forge 47.4.10**, Java 17, ForgeGradle. Copy the gradle setup from `Jump Jet Mod/Source_Code_v2.11.0/` (same versions).
- **New mod**, new folder: `Mod Minecraft Creator/Youjo Senki Arms/`. Suggested mod id `youjoarms`, package `com.youjoarms`.
- **TACZ is a required dependency** (`mandatory=true` in `mods.toml`). The TACZ jar is at `~/Library/Application Support/minecraft/mods/tacz-1.20.1-1.1.6-hotfix.jar`; put it on the compile classpath as a local `compileOnly`/`runtimeOnly` file dependency (or via CurseMaven, pinned to 1.1.6).
- Do NOT depend on the existing `youjosenki` (Jump Jet / flight unit) mod. Optional soft integration later; it is out of scope now.
- No mixins into TACZ unless an event cannot do the job. If you add one, explain why in the code.

## Step 0: verify the TACZ API first (do not guess)
Unzip the TACZ jar into a scratch dir and inspect:
1. The `com.tacz.guns.api` package: list the real event classes (expected names include `GunShootEvent`, `GunFireEvent`, `EntityHurtByGunEvent`, `EntityKillByGunEvent`, `GunReloadEvent`; **confirm them**), what they expose (shooter, gun stack, gun id, bullet entity?), and whether they are cancelable.
2. The bundled default gun pack (`assets/tacz/custom/` or similar): copy its exact folder layout and JSON schema for **gun index, gun data, gun display, ammo index/display, bedrock model, animation, sounds, lang**. Base the new pack on a real built-in bolt-action rifle if one exists.
3. How the bullet tracer color is configured (gun display / ammo display tracer color field). Record your findings in `Youjo Senki Arms/docs/TACZ_API_NOTES.md` before writing code.

## Part A: Gun pack (data only)
Ship the pack **inside the mod jar** (check how TACZ discovers packs from mod jars in 1.1.6; if it doesn't, generate the pack into `tacz/` on first launch).

Guns (start with #1 fully working, others can be stubs with placeholder models):
1. **Kar98k**: bolt-action, 5-round stripper clip, bayonet. **Main gun, do it first.**
2. Gewehr 98 (longer WWI variant).
3. Mauser C96 (pistol).
4. MP18 or MP40 (SMG).
5. A heavy anti-materiel/"artillery" rifle (e.g. Mauser T-Gewehr) used for artillery formulas.

Each gun needs: Bedrock model (blocky TACZ style, wood + blued steel), first-person + third-person display, idle/shoot/bolt/reload/inspect animations, sounds (placeholder OK, note them in the README), and a lang entry.

Ammo (TACZ ammo items):
- `7.92x57mm` standard: **thin colored streak tracer** (warm yellow-white).
- `7.92x57mm` Elenium-infused (special): different tracer color (cyan/blue), higher damage.
- `13mm` for the heavy rifle.

Tracers should read as **long thin colored lines**, not dots. Use TACZ's tracer settings; if they can't make long streaks, add a client-side trail renderer in Part B.

## Part B: Java mod (casting system)
Keep it small and event-driven.

1. **Mana:** a simple player capability (`int mana`, max 100, regen per tick, synced S2C). A HUD bar shown only while holding a `youjoarms` gun.
2. **Cast key** (default `R`-adjacent free key, e.g. `G`, rebindable): hold to charge a formula while holding a youjoarms gun. Release cancels it; firing while charged consumes it. Cycle the selected formula with another key (e.g. `V`).
3. **Formulas** (enum, data per entry: mana cost, charge ticks, circle color):
   - `NONE`: normal shot.
   - `EXPLOSIVE`: small explosion on hit (no block damage by default; config toggle).
   - `PIERCING`: extra damage plus armor penetration.
   - `ARTILLERY` (heavy rifle only, or any gun with high cost): spawns **our own projectile entity**: arcing shell with a glowing streak trail, large AoE explosion on impact. Cancel or replace the TACZ bullet if the event allows it; otherwise fire it alongside.
4. **Magic circle VFX** (client): while charging, render 1–3 flat rotating circle quads in front of the muzzle (camera-facing/aim-aligned), glowing additive texture, plus particles, scaling up with charge %. Show it to other players too (sync charge state via packet). Textures: procedurally generated runic circles (PNG via a Python script in `tools/`, like the repo's other asset scripts).
5. **Hook into TACZ** via the events verified in Step 0: on shoot by a player with a charged formula and enough mana, spend mana, apply the formula effect, play the cast-release sound and particles.
6. **Config** (`forge` common config): mana max/regen, per-formula cost and damage, explosion block damage on/off.

## Deliverables / done when
- `./gradlew build` succeeds and produces `youjoarms-0.1.0.jar`.
- Launch with `./gradlew runClient` (TACZ on runtime classpath): the Kar98k appears in the TACZ gun workbench/creative tab, fires with a streak tracer, and reloads with stripper-clip animation.
- Holding the cast key shows the magic circle at the muzzle; firing with `EXPLOSIVE` spends mana and explodes on hit; `ARTILLERY` fires the arcing shell.
- `README.md` lists: features, keybinds, what is placeholder (models/sounds), and the TACZ version tested.
- `docs/TACZ_API_NOTES.md` from Step 0.

## Out of scope (do not build now)
Flight-unit integration, NPC mage enemies, crafting balance beyond basic recipes, 1.21.1 port.
