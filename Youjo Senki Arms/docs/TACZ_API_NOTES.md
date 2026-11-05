# TACZ API & Gun Pack Architecture Notes

Documenting findings from inspecting `tacz-1.20.1-1.1.6-hotfix.jar` to guide `Youjo Senki Arms` (`youjoarms`).

---

## 1. TACZ Events (`com.tacz.guns.api.event.*`)

TACZ registers custom Forge events posted to `MinecraftForge.EVENT_BUS`:

### Common Events
1. **`com.tacz.guns.api.event.common.GunShootEvent`**
   - **Superclass**: `net.minecraftforge.eventbus.api.Event` (implements `KubeJSGunEventPoster`)
   - **isCancelable()**: `true`
   - **Getters**:
     - `LivingEntity getShooter()`
     - `ItemStack getGunItemStack()`
     - `LogicalSide getLogicalSide()`
   - **Usage**: Fired when a gun trigger is pressed to shoot. If canceled, bullet firing is prevented. Perfect for replacing the standard shot with custom projectiles (e.g. ARTILLERY formula) or checking mana conditions before firing!

2. **`com.tacz.guns.api.event.common.GunFireEvent`**
   - **isCancelable()**: `true`
   - Similar to shoot event, fires on firing logic execution.

3. **`com.tacz.guns.api.event.common.EntityHurtByGunEvent` (and `$Pre`, `$Post`)**
   - **`EntityHurtByGunEvent$Pre`**:
     - **Getters**:
       - `Entity getBullet()`: projectile entity (`EntityKineticBullet`)
       - `Entity getHurtEntity()`: target damaged
       - `LivingEntity getAttacker()`: shooter
       - `ResourceLocation getGunId()`: e.g. `youjoarms:kar98k`
       - `float getAmount()`, `float getBaseAmount()`
       - `DamageSource getDamageSource(GunDamageSourcePart part)`
       - `boolean isHeadShot()`, `float getHeadshotMultiplier()`
     - **Setters in `$Pre`**:
       - `setBaseAmount(float)`
       - `setDamageSource(GunDamageSourcePart, DamageSource)`
       - `setHeadshot(boolean)`
     - **Usage**: Modifying damage for PIERCING formula, checking spell formula buffs on bullet impact.

4. **`com.tacz.guns.api.event.server.AmmoHitBlockEvent`**
   - **isCancelable()**: `true`
   - **Getters**:
     - `Level getLevel()`
     - `BlockHitResult getHitResult()`
     - `BlockState getState()`
     - `EntityKineticBullet getAmmo()`
   - **Usage**: Triggering EXPLOSIVE formulas when a bullet hits blocks.

---

## 2. Gun Pack Layout & Registration

TACZ 1.1.6 loads external gun packs via:
- Directory `<gameDir>/tacz/`
- Also scans `ResourceManager.EXTRA_ENTRIES` registered via:
  ```java
  com.tacz.guns.api.resource.ResourceManager.registerExportResource(MyMod.class, "/tacz_youjoarms");  // needs the leading slash: it is passed to Class.getResource
  ```
  On first load (or if exported), TACZ extracts the folder inside the jar (`assets/tacz_youjoarms` or classpath root) into `tacz/`!
  To guarantee it always loads seamlessly in dev and prod without relying solely on first-run export, we can register it via `registerExportResource` AND ensure files exist or provide a fallback copy on `FMLCommonSetupEvent`.

### Pack Folder Structure:
```
<pack_root>/
  gunpack.meta.json
  data/
    <namespace>/
      index/
        guns/
          kar98k.json
        ammo/
          7_92x57.json
      data/
        guns/
          kar98k_data.json
        ammo/
          7_92x57_data.json
  assets/
    <namespace>/
      display/
        guns/
          kar98k_display.json
        ammo/
          7_92x57_display.json
      models/
        gun/
          kar98k_geo.json
      textures/
        gun/uv/
          kar98k.png
      animations/
        kar98k.animation.json
      sounds/
        ...
```

---

## 3. Tracer Configuration & Color

In TACZ, tracer colors can be configured in:
1. **Ammo Display** (`assets/<namespace>/display/ammo/<id>_display.json`):
   ```json
   {
     "tracer_color": "#FFF59D"
   }
   ```
2. **Gun Display** (`assets/<namespace>/display/guns/<id>_display.json`):
   ```json
   {
     "tracer_color": "#00E5FF"
   }
   ```
3. **Gun Data / Bullet Data** (`data/<namespace>/data/guns/<id>_data.json`):
   ```json
   "bullet": {
     "tracer_count_interval": 0, // 0 = every shot has a tracer!
     "speed": 280,
     ...
   }
   ```
4. **EntityKineticBullet** supports:
   `TRACER_COLOR_OVERRIDER_KEY` (`"TracerColor"`) and `TRACER_SIZE_OVERRIDER_KEY` in persistent data/tags if needed dynamically, or custom trail particles!
