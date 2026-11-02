# Prompt: Trooper Titan redesign + cheap Trooper beacon

Repo: `Titan Combat/` (Forge 1.20.1 + GeckoLib mod). Work only on the Trooper. Do not touch other titans.

## Reference
`promo/trooper_showcase.jpg` is the target look ("MP-01 Trooper Titan"). Today's in-game model is blocky, flat and ugly next to it. Titanfall titans (Atlas/Ogre chassis) are also good style references.

Key traits to copy:
- Hunched, top-heavy torso. A boxy cockpit hull with a roll cage on top and one green visor slit in front.
- Two exhaust stacks on the back that come up above the shoulders.
- Big boxy shoulder pads with "MP-01" + chevron decals and yellow/black hazard stripes on the bottom edge.
- Thick pistons in the arms. **Right arm: a big spiral drill.** **Left arm: a 3-finger hydraulic claw.**
- Digitigrade-ish legs, with an "X" plate on each knee, hazard stripes, and wide two-part feet.
- Colors: olive drab, gunmetal grey frame, rust/wear on the edges, a glowing green visor.

## Files
- Model: `src/main/resources/assets/titancombat/geo/trooper_titan.geo.json` and the cockpit model `geo/cockpit/trooper_titan_1st.geo.json`
- Animations: `animations/trooper_titan.animation.json` and `animations/cockpit/trooper_titan_1st.animation.json`. **Keep the bone names** the animations and Java use (`titan`, `body1..3`, arm/leg bones, `skill_locator`, etc.). Grep Java/animations before you rename anything.
- Textures: `textures/entity/titan/trooper/trooper_titan.png` + `trooper_titan_1..8.png` (paint variants)
- Generator: `../scratch/build_trooper_assets.py`. It builds the geo and textures. **Edit this generator and re-run it. Do not hand-edit the JSON.**
- Entity/stats: `entity/TrooperTitanEntity.java`, `entity/TitanClass.java` (TROOPER)
- Preview: `tools/model_viewer.html` (launch config `titan-viewer` in `.claude/launch.json`)

## Tasks
1. **Redesign the model** to match the traits above. Use more cubes with real silhouette and depth: bevel-like stepped plates, pistons, the drill (stacked tapered rings) and the claw (3 jointed fingers). Stay in the same scale and footprint so the hitbox, seat offset (`TitanClass` seat offsets) and the 1st-person cockpit still line up.
2. **Repaint the texture**: panel lines, edge wear and rust, hazard stripes, the MP-01 decal, and an emissive green visor (use the same glowmask/emissive layer the other titans use, if there is one).
3. **Paint variants**: regenerate all 8 variants with the new UV. Each one gets a clearly different color scheme (olive, desert tan, arctic white, navy, crimson, urban grey, black ops, orange industrial). They must work with the existing `PaintSprayCanItem` / color selection the same way the other titans' variants do.
4. **Equipment visuals**: make the drill and claw read clearly. If Trooper weapons render through `TitanWeapon` / weapon layers, make them fit the new arms.
5. **New cheap summon item `trooper_beacon`** ("Trooper Deployment Beacon"):
   - It does everything `TitanDropBeaconItem` does (summon/drop, recall, owner binding, tooltip, cooldown) but spawns **only** the Trooper. It has no class cycling.
   - Remove `TROOPER` from the main Drop Beacon's class cycling, so Trooper is only reachable through the new beacon.
   - Recipe: change `data/titancombat/recipes/trooper_assembly.json` to output `titancombat:trooper_beacon` with a **much cheaper** recipe (for example: iron ingots + redstone + 1 hydraulic_actuator; no chassis_frame/cockpit_module/iron_block).
   - Register it in `ModItems` and the creative tab. Add the item model, an item texture (make it with `tools/generate_item_textures.py`, olive with a green light), and lang keys in **both** `en_us.json` and `th_th.json`.
   - If `HangarTransponderItem`, `ClientAutoTest`, or anything else checks `instanceof TitanDropBeaconItem`, make it accept the new item too. Grep for it.
6. Build with `./gradlew build`. Check it in `tools/model_viewer.html` and take a screenshot. If `ClientAutoTest` can screenshot the Trooper in game, do that too.

## Done when
- The build passes, and the Trooper looks close to the showcase in the viewer, in all 8 colors.
- The new beacon crafts cheaply, summons only a Trooper, and every function of the old beacon works.
- Nothing changed for the other titans.
