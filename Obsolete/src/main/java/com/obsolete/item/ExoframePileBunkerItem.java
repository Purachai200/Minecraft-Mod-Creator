package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.sound.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * Hydraulic pile bunker: each 8-gauge drive charge fires the steel stake forward. Short reach, huge single-target
 * damage and knockback, and it punches through the block in front (doors, walls up to stone hardness).
 */
public class ExoframePileBunkerItem extends ExoframeWeaponItem {
    private static final double REACH = 2.6D;               // blocks ahead of the exoframe front, before model scale
    private static final float STAKE_DAMAGE = 60.0F;
    private static final float MAX_BREACH_HARDNESS = 3.0F;  // stone / doors / planks; not obsidian

    public ExoframePileBunkerItem(Properties properties) {
        super(properties.stacksTo(1), 22, "weapon_pile_bunker");
    }

    @Override
    public int getMagazineCapacity() {
        return 6;
    }

    @Override
    public int getReloadDurationTicks() {
        return 55;
    }

    @Override
    public ExoframeAmmoItem.AmmoType getRequiredAmmoType() {
        return ExoframeAmmoItem.AmmoType.SHOTGUN_SLUG;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        Level level = exoframe.level();
        if (!checkOrConsumeAmmo(exoframe, pilot, true)) {
            return false;
        }
        exoframe.performMeleeAttack(pilot); // punch animation + base hit

        Vec3 forward = pilot.getLookAngle().normalize();
        Vec3 start = exoframe.position().add(0, 1.2D * ExoframeEntity.MODEL_SCALE, 0);
        Vec3 tip = start.add(forward.scale(REACH * ExoframeEntity.MODEL_SCALE));
        AABB lane = new AABB(start, tip).inflate(0.9D);
        List<LivingEntity> hits = level.getEntitiesOfClass(LivingEntity.class, lane,
                e -> e != exoframe && e != pilot && !exoframe.isAlliedTo(e) && e.isAlive());
        for (LivingEntity target : hits) {
            target.hurt(exoframe.damageSources().mobAttack(exoframe), STAKE_DAMAGE);
            target.setDeltaMovement(forward.scale(2.2D).add(0, 0.4D, 0));
            target.hurtMarked = true;
        }

        BlockHitResult blockHit = level.clip(new ClipContext(start, tip, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, pilot));
        if (blockHit.getType() == HitResult.Type.BLOCK && level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) {
            BlockPos pos = blockHit.getBlockPos();
            BlockState state = level.getBlockState(pos);
            float hardness = state.getDestroySpeed(level, pos);
            if (hardness >= 0.0F && hardness <= MAX_BREACH_HARDNESS) {
                level.destroyBlock(pos, true, pilot);
            }
        }

        Vec3 fx = hits.isEmpty() ? tip : hits.get(0).position().add(0, hits.get(0).getBbHeight() * 0.5D, 0);
        if (level instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.EXPLOSION, fx.x, fx.y, fx.z, 1, 0, 0, 0, 0.0);
            serverLevel.sendParticles(ParticleTypes.CRIT, fx.x, fx.y, fx.z, 18, 0.4, 0.4, 0.4, 0.4);
            Vec3 vent = start.subtract(forward.scale(0.4D));
            serverLevel.sendParticles(ParticleTypes.CLOUD, vent.x, vent.y, vent.z, 6, 0.15, 0.15, 0.15, 0.05);
        }
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_SHOTGUN_FIRE.get(), SoundSource.PLAYERS, 3.0F, 0.6F);
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_IMPACT_METAL.get(), SoundSource.PLAYERS, 3.5F, 0.7F);
        exoframe.triggerPilotCameraShake(1.2F, 8);
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Hydraulic breaching ram: 60 damage, breaks the block ahead").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "8-Gauge Heavy Breaching Slugs (drive charges)").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
