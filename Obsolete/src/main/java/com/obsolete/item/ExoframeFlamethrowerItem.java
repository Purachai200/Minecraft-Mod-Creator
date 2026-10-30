package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.sound.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseFireBlock;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExoframeFlamethrowerItem extends ExoframeWeaponItem {
    private int burstCounter = 0;

    public ExoframeFlamethrowerItem(Properties properties) {
        super(properties.stacksTo(1), 2, "weapon_flamethrower");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        ItemStack util = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (util.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.NAPALM_CANISTER) {
            if (consume) {
                burstCounter++;
                if (burstCounter >= 8) {
                    burstCounter = 0;
                    util.shrink(1);
                    exoframe.getModularInventory().setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), util);
                }
            }
            return true;
        }
        for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
            ItemStack s = pilot.getInventory().getItem(i);
            if (s.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.NAPALM_CANISTER) {
                if (consume) {
                    burstCounter++;
                    if (burstCounter >= 8) {
                        burstCounter = 0;
                        s.shrink(1);
                    }
                }
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        if (!checkOrConsumeAmmo(exoframe, pilot, true)) {
            pilot.displayClientMessage(Component.literal("§c[Munitions Depleted] Required: Liquid Napalm Canister"), true);
            return false;
        }

        Level level = exoframe.level();
        Vec3 look = pilot.getLookAngle();
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 nozzlePos = exoframe.position().add(0, 1.7D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.68D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(1.1D * ExoframeEntity.MODEL_SCALE));

        if (level instanceof ServerLevel serverLevel) {
            // Spawn flame cone particles
            for (int dist = 2; dist <= 12; dist += 2) {
                double spread = dist * 0.15D;
                Vec3 pPos = nozzlePos.add(forward.scale(dist));
                for (int p = 0; p < 4; p++) {
                    double ox = (serverLevel.random.nextDouble() - 0.5D) * spread;
                    double oy = (serverLevel.random.nextDouble() - 0.5D) * spread;
                    double oz = (serverLevel.random.nextDouble() - 0.5D) * spread;
                    serverLevel.sendParticles(ParticleTypes.FLAME, pPos.x + ox, pPos.y + oy, pPos.z + oz, 1, 0, 0, 0, 0.05);
                    if (serverLevel.random.nextFloat() < 0.3F) {
                        serverLevel.sendParticles(ParticleTypes.LAVA, pPos.x + ox, pPos.y + oy, pPos.z + oz, 1, 0, 0, 0, 0.02);
                    }
                }
            }

            // Damage and ignite entities in cone
            Vec3 coneCenter = nozzlePos.add(forward.scale(6.0D));
            AABB coneBox = new AABB(coneCenter.x - 5.0, coneCenter.y - 3.0, coneCenter.z - 5.0,
                    coneCenter.x + 5.0, coneCenter.y + 3.0, coneCenter.z + 5.0);
            List<LivingEntity> targets = serverLevel.getEntitiesOfClass(LivingEntity.class, coneBox,
                    e -> e != exoframe && e != pilot && e.isAlive());

            for (LivingEntity target : targets) {
                Vec3 toTarget = target.position().subtract(nozzlePos).normalize();
                if (toTarget.dot(forward) > 0.65D) {
                    target.hurt(level.damageSources().inFire(), 8.0F);
                    target.setSecondsOnFire(6);
                }
            }

            // Ignite ground at impact
            BlockPos ground = BlockPos.containing(nozzlePos.add(forward.scale(8.0D)));
            if (serverLevel.isEmptyBlock(ground) && BaseFireBlock.canBePlacedAt(serverLevel, ground, net.minecraft.core.Direction.UP)) {
                serverLevel.setBlockAndUpdate(ground, BaseFireBlock.getState(serverLevel, ground));
            }
        }

        level.playSound(null, exoframe.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 2.0F, 0.8F);
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.obsolete.exoframe_flamethrower").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "Liquid Napalm Canister").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
