package com.titancombat.entity;

import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/**
 * Shade Class Titan: mass-produced cloaked infiltrator on the Trooper skeleton.
 * The Defense key toggles an optical cloak instead of the shield matrix: the frame turns invisible
 * (TitanRenderer draws it as a faint shimmer) and hostile mobs drop it as a target. The cloak runs
 * up to 10 s, drains shield, and breaks on firing or taking damage.
 */
public class ShadeTitanEntity extends BaseTitanEntity {
    private static final int CLOAK_TICKS = 200;
    private static final int CLOAK_COOLDOWN = 300;
    private static final float CLOAK_DRAIN = 0.15F;

    private int cloakTicks = 0;
    private int cloakCooldown = 0;

    public ShadeTitanEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    @Override
    public TitanClass getTitanClass() {
        return TitanClass.SHADE;
    }

    @Override
    public void toggleDefenseMatrix(Player pilot) {
        if (this.level().isClientSide) return;
        if (cloakTicks > 0) {
            decloak();
        } else if (cloakCooldown > 0) {
            pilot.displayClientMessage(Component.literal("§7[CLOAK] Recharging: " + (cloakCooldown / 20 + 1) + "s"), true);
        } else if (getShield() > 5.0F) {
            cloakTicks = CLOAK_TICKS;
            setInvisible(true);
            pilot.displayClientMessage(Component.literal("§b[CLOAK] Optical camouflage engaged"), true);
            this.level().playSound(null, blockPosition(), SoundEvents.ILLUSIONER_MIRROR_MOVE, SoundSource.PLAYERS, 1.5F, 0.8F);
        } else {
            pilot.displayClientMessage(Component.translatable("message.titancombat.shield_down"), true);
        }
    }

    /** GeckoLib skips rendering entities that are invisible to the viewer; keep it drawing so TitanRenderer can shimmer it. */
    @Override
    public boolean isInvisibleTo(Player player) {
        return false;
    }

    public boolean isCloaked() {
        return isInvisible();
    }

    private void decloak() {
        if (cloakTicks <= 0) return;
        cloakTicks = 0;
        cloakCooldown = CLOAK_COOLDOWN;
        setInvisible(false);
        this.level().playSound(null, blockPosition(), SoundEvents.ILLUSIONER_PREPARE_MIRROR, SoundSource.PLAYERS, 1.2F, 1.2F);
    }

    @Override
    public void tick() {
        super.tick();
        if (this.level().isClientSide) return;
        if (cloakCooldown > 0) cloakCooldown--;
        if (cloakTicks > 0) {
            cloakTicks--;
            setShield(Math.max(0.0F, getShield() - CLOAK_DRAIN));
            if (cloakTicks == 0 || getShield() <= 0.0F) {
                cloakTicks = 1;
                decloak();
                return;
            }
            // Mobs keep re-acquiring targets; while cloaked, keep wiping any lock on the titan or its pilot.
            if (this.tickCount % 5 == 0) {
                Entity pilot = getControllingPassenger();
                for (Mob mob : this.level().getEntitiesOfClass(Mob.class, getBoundingBox().inflate(48.0D))) {
                    if (mob.getTarget() != null && (mob.getTarget() == this || mob.getTarget() == pilot)) {
                        mob.setTarget(null);
                    }
                }
            }
        }
    }

    @Override
    public boolean firePrimaryWeapon(Player pilot) {
        decloak();
        return super.firePrimaryWeapon(pilot);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hit = super.hurt(source, amount);
        if (hit && !this.level().isClientSide) decloak();
        return hit;
    }
}
