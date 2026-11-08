package com.titancombat.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.DyeItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public abstract class BaseMechEntity extends PathfinderMob {

    // Multiplayer-synced data accessors
    public static final EntityDataAccessor<Byte> DATA_MECH_STATE =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.BYTE);
    public static final EntityDataAccessor<Integer> DATA_FACTION_ID =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_PRIMARY_COLOR =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_SECONDARY_COLOR =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Float> DATA_SHIELD =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.FLOAT);
    public static final EntityDataAccessor<Float> DATA_MAX_SHIELD =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.FLOAT);
    public static final EntityDataAccessor<Float> DATA_DASH_CHARGE =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.FLOAT);
    public static final EntityDataAccessor<Float> DATA_CORE_CHARGE =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.FLOAT);
    public static final EntityDataAccessor<Integer> DATA_OVERDRIVE_TICKS =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Boolean> DATA_DEFENSE_ACTIVE =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.BOOLEAN);
    public static final int DEFAULT_MAX_ENERGY = 50000;
    public static final EntityDataAccessor<Integer> DATA_ENERGY =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_MAX_ENERGY =
            SynchedEntityData.defineId(BaseMechEntity.class, EntityDataSerializers.INT);

    // Timers & internal mechanics
    protected int shieldRegenCooldown = 0;
    protected int landingStandupTimer = 0;
    protected int doomedCountdown = 200; // 10 seconds before explosion if doomed
    protected int warpDefenseTicks = 0;

    public BaseMechEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(2.0F); // Can walk over 2-block obstacles smoothly
        this.setPersistenceRequired();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 200.0D) // Heavy mech hull HP
                .add(Attributes.MOVEMENT_SPEED, 0.28D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                .add(Attributes.ARMOR, 20.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 12.0D)
                .add(Attributes.ATTACK_DAMAGE, 18.0D);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_MECH_STATE, MechState.IDLE.getId());
        this.entityData.define(DATA_FACTION_ID, MechFaction.APEX_VANGUARD.getId());
        this.entityData.define(DATA_PRIMARY_COLOR, MechFaction.APEX_VANGUARD.getDefaultPrimaryColor());
        this.entityData.define(DATA_SECONDARY_COLOR, MechFaction.APEX_VANGUARD.getEmissiveColor());
        this.entityData.define(DATA_SHIELD, 100.0F);
        this.entityData.define(DATA_MAX_SHIELD, 100.0F);
        this.entityData.define(DATA_DASH_CHARGE, 100.0F);
        this.entityData.define(DATA_CORE_CHARGE, 0.0F);
        this.entityData.define(DATA_OVERDRIVE_TICKS, 0);
        this.entityData.define(DATA_DEFENSE_ACTIVE, false);
        this.entityData.define(DATA_ENERGY, 0);
        this.entityData.define(DATA_MAX_ENERGY, DEFAULT_MAX_ENERGY);
    }

    public MechState getMechState() {
        return MechState.byId(this.entityData.get(DATA_MECH_STATE));
    }

    public void setMechState(MechState state) {
        this.entityData.set(DATA_MECH_STATE, state.getId());
    }

    public int getFactionId() {
        return this.entityData.get(DATA_FACTION_ID);
    }

    public void setFaction(MechFaction faction) {
        this.entityData.set(DATA_FACTION_ID, faction.getId());
        this.entityData.set(DATA_PRIMARY_COLOR, faction.getDefaultPrimaryColor());
        this.entityData.set(DATA_SECONDARY_COLOR, faction.getEmissiveColor());
    }

    public int getPrimaryColor() {
        return this.entityData.get(DATA_PRIMARY_COLOR);
    }

    public void setPrimaryColor(int color) {
        this.entityData.set(DATA_PRIMARY_COLOR, color);
    }

    public int getSecondaryColor() {
        return this.entityData.get(DATA_SECONDARY_COLOR);
    }

    public float getShield() {
        return this.entityData.get(DATA_SHIELD);
    }

    public void setShield(float shield) {
        this.entityData.set(DATA_SHIELD, Mth.clamp(shield, 0.0F, getMaxShield()));
    }

    public float getMaxShield() {
        return this.entityData.get(DATA_MAX_SHIELD);
    }

    public float getDashCharge() {
        return this.entityData.get(DATA_DASH_CHARGE);
    }

    public void setDashCharge(float charge) {
        this.entityData.set(DATA_DASH_CHARGE, Mth.clamp(charge, 0.0F, 100.0F));
    }

    public float getCoreCharge() {
        return this.entityData.get(DATA_CORE_CHARGE);
    }

    public void setCoreCharge(float charge) {
        this.entityData.set(DATA_CORE_CHARGE, Mth.clamp(charge, 0.0F, 100.0F));
    }

    public void addCoreCharge(float amount) {
        setCoreCharge(getCoreCharge() + amount);
    }

    public int getOverdriveTicks() {
        return this.entityData.get(DATA_OVERDRIVE_TICKS);
    }

    public void setOverdriveTicks(int ticks) {
        this.entityData.set(DATA_OVERDRIVE_TICKS, Math.max(0, ticks));
    }

    public boolean isOverdriveActive() {
        return getOverdriveTicks() > 0;
    }

    public boolean isDefenseActive() {
        return this.entityData.get(DATA_DEFENSE_ACTIVE);
    }

    public void setDefenseActive(boolean active) {
        this.entityData.set(DATA_DEFENSE_ACTIVE, active);
    }

    public int getEnergy() {
        return this.entityData.get(DATA_ENERGY);
    }

    public void setEnergy(int energy) {
        this.entityData.set(DATA_ENERGY, Mth.clamp(energy, 0, getMaxEnergy()));
    }

    public int getMaxEnergy() {
        return this.entityData.get(DATA_MAX_ENERGY);
    }

    public void setMaxEnergy(int maxEnergy) {
        this.entityData.set(DATA_MAX_ENERGY, Math.max(1, maxEnergy));
    }

    public void addEnergy(int amount) {
        setEnergy(getEnergy() + amount);
    }

    public boolean consumeEnergy(int amount) {
        int cur = getEnergy();
        if (cur >= amount) {
            setEnergy(cur - amount);
            return true;
        }
        return false;
    }

    public int getWarpDefenseTicks() {
        return warpDefenseTicks;
    }

    public void setWarpDefenseTicks(int ticks) {
        this.warpDefenseTicks = Math.max(0, ticks);
        if (this.warpDefenseTicks > 0) {
            setDefenseActive(true);
        }
    }

    public boolean activateCoreOverdrive(@Nullable Player pilot) {
        if (getCoreCharge() < 100.0F || isOverdriveActive()) {
            return false;
        }
        setCoreCharge(0.0F);
        setOverdriveTicks(200); // 10 seconds of max overdrive
        setShield(getMaxShield()); // Instant full overshield recharge

        if (!this.level().isClientSide) {
            this.level().playSound(null, this.blockPosition(), SoundEvents.WARDEN_SONIC_BOOM, SoundSource.PLAYERS, 2.0F, 1.4F);
            this.level().playSound(null, this.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 2.5F, 1.2F);
            if (pilot != null) {
                pilot.sendSystemMessage(Component.translatable("message.titancombat.core_engaged"));
            }
        }
        return true;
    }

    public void toggleDefenseMatrix(Player pilot) {
        if (!isDefenseActive()) {
            if (getShield() > 5.0F) {
                setDefenseActive(true);
                if (!this.level().isClientSide) {
                    pilot.sendSystemMessage(Component.translatable("message.titancombat.defense_on"));
                    this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.5F, 1.2F);
                }
            } else {
                if (!this.level().isClientSide) {
                    pilot.sendSystemMessage(Component.translatable("message.titancombat.shield_down"));
                    this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.2F, 1.4F);
                }
            }
        } else {
            setDefenseActive(false);
            if (!this.level().isClientSide) {
                pilot.sendSystemMessage(Component.translatable("message.titancombat.defense_off"));
                this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_DOOR_OPEN, SoundSource.PLAYERS, 1.0F, 1.4F);
            }
        }
    }

    @Override
    public boolean isAlliedTo(Entity other) {
        if (other instanceof BaseMechEntity otherMech) {
            return this.getFactionId() == otherMech.getFactionId();
        }
        if (other instanceof Player player) {
            // Check if player is allied through riding or faction
            if (this.hasPassenger(player)) return true;
        }
        return super.isAlliedTo(other);
    }

    @Override
    public void tick() {
        super.tick();

        MechState state = getMechState();

        if (state == MechState.DROPPING) {
            handleOrbitalDrop();
        } else if (state == MechState.LANDED) {
            if (!this.level().isClientSide) {
                if (++landingStandupTimer > 40) { // 2 seconds kneeled standby
                    setMechState(hasControllingPassenger() ? MechState.PILOTED : MechState.IDLE);
                }
            }
        }

        // Core Overdrive timer & VFX
        int odTicks = getOverdriveTicks();
        if (odTicks > 0) {
            if (!this.level().isClientSide) {
                setOverdriveTicks(odTicks - 1);
                if (odTicks - 1 == 0) {
                    Entity p = this.getFirstPassenger();
                    if (p instanceof Player pilot) {
                        pilot.sendSystemMessage(Component.translatable("message.titancombat.core_exhausted"));
                    }
                    this.level().playSound(null, this.blockPosition(), SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 1.8F, 1.2F);
                }
            } else {
                if (this.random.nextFloat() < 0.4F) {
                    this.level().addParticle(ParticleTypes.ELECTRIC_SPARK,
                            this.getX() + (this.random.nextDouble() - 0.5D) * 2.2D,
                            this.getY() + 1.0D + this.random.nextDouble() * 2.5D,
                            this.getZ() + (this.random.nextDouble() - 0.5D) * 2.2D,
                            0, 0.1D, 0);
                }
            }
        }

        // Tactical Defense Matrix maintenance & shield drain
        if (isDefenseActive()) {
            if (!this.level().isClientSide) {
                if (warpDefenseTicks > 0) {
                    warpDefenseTicks--;
                    // During warp arrival defense, keep shield fully topped up
                    if (getShield() < getMaxShield()) {
                        setShield(getMaxShield());
                    }
                } else if (this.tickCount % 4 == 0) {
                    float currentShield = getShield();
                    if (currentShield <= 1.0F) {
                        setShield(0.0F);
                        setDefenseActive(false);
                        Entity p = this.getFirstPassenger();
                        if (p instanceof Player pilot) {
                            pilot.sendSystemMessage(Component.translatable("message.titancombat.defense_off"));
                        }
                        this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BREAK, SoundSource.PLAYERS, 1.5F, 1.2F);
                    } else {
                        setShield(currentShield - 1.0F);
                    }
                }
            } else {
                if (this.random.nextFloat() < (warpDefenseTicks > 0 ? 0.7F : 0.3F)) {
                    this.level().addParticle(ParticleTypes.ENCHANTED_HIT,
                            this.getX() + (this.random.nextDouble() - 0.5D) * 2.0D,
                            this.getY() + 1.2D + this.random.nextDouble() * 2.0D,
                            this.getZ() + (this.random.nextDouble() - 0.5D) * 2.0D,
                            0, 0.05D, 0);
                }
                if (warpDefenseTicks > 0 && this.random.nextFloat() < 0.45F) {
                    this.level().addParticle(ParticleTypes.ELECTRIC_SPARK,
                            this.getX() + (this.random.nextDouble() - 0.5D) * 3.6D,
                            this.getY() + 0.5D + this.random.nextDouble() * 3.6D,
                            this.getZ() + (this.random.nextDouble() - 0.5D) * 3.6D,
                            0, 0.05D, 0);
                }
            }
        }

        // Shield & Dash regeneration & Core passive buildup (optimized: batched every 4 ticks)
        if (!this.level().isClientSide) {
            if (this.tickCount % 4 == 0) {
                if (shieldRegenCooldown > 0) {
                    shieldRegenCooldown = Math.max(0, shieldRegenCooldown - 4);
                } else if (getShield() < getMaxShield() && !isDefenseActive()) {
                    if (consumeEnergy(5)) {
                        setShield(getShield() + 2.0F); // 10 shield per second, drains 25 FE/s
                    }
                }

                if (getDashCharge() < 100.0F) {
                    setDashCharge(getDashCharge() + 3.2F); // ~6 seconds for full recovery
                }

                // Passive Core charge buildup when piloted and not in Overdrive (+1.25% per second)
                if (hasControllingPassenger() && !isOverdriveActive() && getCoreCharge() < 100.0F) {
                    float oldCharge = getCoreCharge();
                    addCoreCharge(0.25F);
                    if (oldCharge < 100.0F && getCoreCharge() >= 100.0F) {
                        Entity p = this.getFirstPassenger();
                        if (p instanceof Player pilot) {
                            pilot.sendSystemMessage(Component.translatable("message.titancombat.core_ready"));
                            this.level().playSound(null, this.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 1.2F, 1.8F);
                        }
                    }
                }
            } else if (shieldRegenCooldown > 0) {
                shieldRegenCooldown--;
            }

            // Doomed state countdown
            if (state == MechState.DOOMED) {
                if (--doomedCountdown <= 0) {
                    explodeAndDestroy();
                } else if (this.tickCount % 3 == 0 && this.random.nextFloat() < 0.4F) {
                    this.level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE,
                            this.getX() + (this.random.nextDouble() - 0.5D),
                            this.getY() + 3.0D,
                            this.getZ() + (this.random.nextDouble() - 0.5D),
                            0, 0.1D, 0);
                }
            }
        }
    }

    protected void handleOrbitalDrop() {
        // High speed downward atmospheric descent
        if (!this.onGround()) {
            this.setDeltaMovement(0, -2.5D, 0);
            if (this.level().isClientSide) {
                for (int i = 0; i < 4; i++) {
                    this.level().addParticle(ParticleTypes.FLAME,
                            this.getX() + (this.random.nextDouble() - 0.5D) * 2.0D,
                            this.getY() + this.random.nextDouble() * 3.0D,
                            this.getZ() + (this.random.nextDouble() - 0.5D) * 2.0D,
                            0, 0.4D, 0);
                }
            }
        } else {
            // Ground Slam Impact!
            if (!this.level().isClientSide) {
                setMechState(MechState.LANDED);
                landingStandupTimer = 0;

                // Kinetic impact shockwave dealing AoE damage to enemies
                AABB impactArea = this.getBoundingBox().inflate(6.0D, 2.0D, 6.0D);
                List<LivingEntity> targets = this.level().getEntitiesOfClass(LivingEntity.class, impactArea,
                        e -> e != this && !this.isAlliedTo(e));

                for (LivingEntity target : targets) {
                    target.hurt(this.damageSources().explosion(this, null), 45.0F);
                    Vec3 knockback = target.position().subtract(this.position()).normalize().scale(1.8D);
                    target.setDeltaMovement(knockback.x, 0.6D, knockback.z);
                }

                this.level().playSound(null, this.blockPosition(), SoundEvents.GENERIC_EXPLODE,
                        SoundSource.HOSTILE, 3.0F, 0.8F);
            }
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (getMechState() == MechState.DROPPING || warpDefenseTicks > 0) {
            if (warpDefenseTicks > 0) {
                this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.5F, 1.2F);
            }
            return false; // Invulnerable during atmospheric drop or warp arrival
        }

        // 1. Tactical Defense Matrix: deflects 80% damage
        if (isDefenseActive()) {
            float blocked = amount * 0.8F;
            amount *= 0.2F;
            float shieldCost = blocked * 0.4F;
            setShield(Math.max(0.0F, getShield() - shieldCost));
            if (getShield() <= 0.0F) {
                setDefenseActive(false);
            }
            this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.5F, 0.9F);
        }

        shieldRegenCooldown = 100; // Reset shield regen timer (5 seconds)

        // 2. Kinetic Overshield Absorption
        float currentShield = getShield();
        if (currentShield > 0) {
            if (this.level().isClientSide) {
                // Shield deflection VFX
                this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.2F, 1.4F);
            }
            if (amount <= currentShield) {
                setShield(currentShield - amount);
                return false;
            } else {
                amount -= currentShield;
                setShield(0.0F);
                // Kinetic Shield Compromised Warning!
                if (!this.level().isClientSide) {
                    this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BREAK, SoundSource.PLAYERS, 1.8F, 0.8F);
                    Entity p = this.getFirstPassenger();
                    if (p instanceof Player pilot) {
                        pilot.sendSystemMessage(Component.translatable("message.titancombat.shield_down"));
                    }
                }
            }
        }

        // Taking damage builds Core Charge (+20% of hull damage taken)
        if (!this.level().isClientSide && !isOverdriveActive()) {
            addCoreCharge(amount * 0.2F);
        }

        boolean damaged = super.hurt(source, amount);

        if (!this.level().isClientSide && this.getHealth() <= (this.getMaxHealth() * 0.15F) && getMechState() != MechState.DOOMED) {
            setMechState(MechState.DOOMED);
            this.level().playSound(null, this.blockPosition(), SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 2.0F, 0.6F);
        }

        return damaged;
    }

    /** Thruster fuel per dash: three dashes from a full tank. */
    public static final float DASH_COST = 100.0F / 3.0F;

    public void performDash(float forward, float strafe) {
        if (getDashCharge() < DASH_COST - 0.01F) return;
        if (getEnergy() < 250) {
            if (this.getFirstPassenger() instanceof Player p && !this.level().isClientSide) {
                p.displayClientMessage(Component.translatable("message.titancombat.reactor_depleted_warning"), true);
            }
            return;
        }
        setDashCharge(Math.max(0.0F, getDashCharge() - DASH_COST));
        consumeEnergy(250);

        float yaw = this.getYRot() * (float) (Math.PI / 180.0);
        Vec3 direction = new Vec3(
                -Mth.sin(yaw) * forward + Mth.cos(yaw) * strafe,
                0,
                Mth.cos(yaw) * forward + Mth.sin(yaw) * strafe
        ).normalize().scale(1.8D);

        this.setDeltaMovement(this.getDeltaMovement().add(direction.x, 0.15D, direction.z));
        this.hasImpulse = true;

        this.level().playSound(null, this.blockPosition(), SoundEvents.FIREWORK_ROCKET_BLAST, SoundSource.PLAYERS, 2.0F, 0.7F);
    }

    public void ejectPilot() {
        Entity passenger = this.getFirstPassenger();
        if (passenger instanceof Player player) {
            player.stopRiding();
            // Launch pilot high into the sky (synergizes with jump jets / gliders)
            player.setDeltaMovement(0, 2.4D, 0);
            player.hurtMarked = true;

            this.level().playSound(null, this.blockPosition(), SoundEvents.GENERIC_EXPLODE, SoundSource.PLAYERS, 2.5F, 1.5F);
            explodeAndDestroy();
        }
    }

    protected void explodeAndDestroy() {
        if (!this.level().isClientSide) {
            this.level().explode(this, this.getX(), this.getY() + 1.5D, this.getZ(), 4.0F, Level.ExplosionInteraction.MOB);
            this.discard();
        }
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);

        // Customize color via Dye
        if (held.getItem() instanceof DyeItem dye) {
            if (!this.level().isClientSide) {
                MechFaction matched = MechFaction.byDye(dye.getDyeColor());
                setFaction(matched);
                // Also assign exact dye RGB color
                float[] rgb = dye.getDyeColor().getTextureDiffuseColors();
                int r = (int) (rgb[0] * 255.0F);
                int g = (int) (rgb[1] * 255.0F);
                int b = (int) (rgb[2] * 255.0F);
                setPrimaryColor((r << 16) | (g << 8) | b);

                if (!player.getAbilities().instabuild) {
                    held.shrink(1);
                }
                this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 1.0F, 1.2F);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // Enter Cockpit
        if (!this.isVehicle() && !player.isPassenger() && getMechState() != MechState.DROPPING) {
            if (!this.level().isClientSide) {
                player.startRiding(this);
                setMechState(MechState.PILOTED);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        return super.mobInteract(player, hand);
    }

    @Nullable
    @Override
    public LivingEntity getControllingPassenger() {
        Entity passenger = this.getFirstPassenger();
        return passenger instanceof LivingEntity living ? living : null;
    }

    @Override
    public void travel(Vec3 travelVector) {
        if (this.isAlive()) {
            LivingEntity rider = this.getControllingPassenger();
            if (this.isVehicle() && rider != null) {
                this.setYRot(rider.getYRot());
                this.yRotO = this.getYRot();
                this.setXRot(rider.getXRot() * 0.5F);
                this.setRot(this.getYRot(), this.getXRot());
                this.yBodyRot = this.getYRot();
                this.yHeadRot = this.yBodyRot;

                if (this.isControlledByLocalInstance()) {
                    travelPiloted(rider, travelVector);
                } else if (rider instanceof Player) {
                    this.setDeltaMovement(Vec3.ZERO);
                }
                return;
            } else if (!this.isVehicle() && getEnergy() <= 0) {
                this.setSpeed(0.0F);
                super.travel(new Vec3(0, travelVector.y, 0));
                return;
            }
        }
        super.travel(travelVector);
    }

    /** Movement while a pilot drives this mech on the controlling client. */
    protected void travelPiloted(LivingEntity rider, Vec3 travelVector) {
        float forward = rider.zza;
        float strafe = rider.xxa * 0.7F;

        if (getEnergy() <= 0) {
            this.setSpeed(0.0F);
            if (Math.abs(forward) > 0.01F || Math.abs(strafe) > 0.01F) {
                if (rider instanceof Player p && this.tickCount % 40 == 0) {
                    p.displayClientMessage(Component.translatable("message.titancombat.reactor_depleted_warning"), true);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.FLINTANDSTEEL_USE, SoundSource.PLAYERS, 1.2F, 0.6F);
                }
            }
            super.travel(new Vec3(0, travelVector.y, 0));
            return;
        }

        if (forward <= 0.0F) {
            forward *= 0.5F; // Slower reverse
        }

        if (!this.level().isClientSide) {
            boolean moving = Math.abs(forward) > 0.01F || Math.abs(strafe) > 0.01F;
            if (moving) {
                int drain = rider.isSprinting() ? 8 : 4;
                consumeEnergy(drain);
            } else if (this.tickCount % 2 == 0) {
                consumeEnergy(1); // Idle consumption: 10 FE/s
            }
        }

        this.setSpeed((float) this.getAttributeValue(Attributes.MOVEMENT_SPEED));
        super.travel(new Vec3(strafe, travelVector.y, forward));
    }

    @Override
    protected void positionRider(Entity passenger, Entity.MoveFunction moveFunction) {
        if (this.hasPassenger(passenger)) {
            // Position pilot securely inside upper chest cockpit
            double cockpitY = this.getY() + 2.8D;
            moveFunction.accept(passenger, this.getX(), cockpitY, this.getZ());
        }
    }

    @Override
    public boolean showVehicleHealth() {
        // Combat Titan Hull & Shield are visualized via the high-tech Sci-Fi Cockpit HUD, NOT animal horse hearts!
        return false;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putByte("MechState", getMechState().getId());
        tag.putInt("FactionId", getFactionId());
        tag.putInt("PrimaryColor", getPrimaryColor());
        tag.putInt("SecondaryColor", getSecondaryColor());
        tag.putFloat("Shield", getShield());
        tag.putFloat("DashCharge", getDashCharge());
        tag.putFloat("CoreCharge", getCoreCharge());
        tag.putInt("OverdriveTicks", getOverdriveTicks());
        tag.putBoolean("DefenseActive", isDefenseActive());
        tag.putInt("WarpDefenseTicks", getWarpDefenseTicks());
        tag.putInt("Energy", getEnergy());
        tag.putInt("MaxEnergy", getMaxEnergy());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("MechState")) setMechState(MechState.byId(tag.getByte("MechState")));
        if (tag.contains("FactionId")) setFaction(MechFaction.byId(tag.getInt("FactionId")));
        if (tag.contains("PrimaryColor")) setPrimaryColor(tag.getInt("PrimaryColor"));
        if (tag.contains("SecondaryColor")) this.entityData.set(DATA_SECONDARY_COLOR, tag.getInt("SecondaryColor"));
        if (tag.contains("Shield")) setShield(tag.getFloat("Shield"));
        if (tag.contains("DashCharge")) setDashCharge(tag.getFloat("DashCharge"));
        if (tag.contains("CoreCharge")) setCoreCharge(tag.getFloat("CoreCharge"));
        if (tag.contains("OverdriveTicks")) setOverdriveTicks(tag.getInt("OverdriveTicks"));
        if (tag.contains("DefenseActive")) setDefenseActive(tag.getBoolean("DefenseActive"));
        if (tag.contains("WarpDefenseTicks")) setWarpDefenseTicks(tag.getInt("WarpDefenseTicks"));
        if (tag.contains("Energy")) setEnergy(tag.getInt("Energy"));
        if (tag.contains("MaxEnergy")) setMaxEnergy(tag.getInt("MaxEnergy"));
    }
}
