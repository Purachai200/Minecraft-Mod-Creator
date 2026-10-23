package com.youjosenki.flight.telemetry;

import com.youjosenki.flight.Config;
import com.youjosenki.flight.client.vfx.FlightVFXHelper;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import com.youjosenki.flight.network.ModNetworking;
import com.youjosenki.flight.network.SyncFlightTelemetryS2CPacket;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.energy.IEnergyStorage;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class FlightStateManager {
    private static final Map<UUID, PlayerFlightData> PLAYER_DATA = new ConcurrentHashMap<>();

    public static class PlayerFlightData {
        public float heat = 0.0F;
        public boolean overheated = false;
        public int boostCooldown = 0;
        public int boostStep = 1;
        public long lastBoostTime = 0;
    }

    public static PlayerFlightData getPlayerData(UUID uuid) {
        return PLAYER_DATA.computeIfAbsent(uuid, k -> new PlayerFlightData());
    }

    public static void clearPlayerData(UUID uuid) {
        PLAYER_DATA.remove(uuid);
    }

    public static void tickServer(ServerPlayer player, EleniumFlightUnitItem item, ItemStack stack, boolean isFlying, boolean isSprinting) {
        PlayerFlightData data = getPlayerData(player.getUUID());
        String unitName = stack.getHoverName().getString();

        // 1. Service Ceiling Dynamics: Enforced only during active flight in the air!
        // Walking or climbing mountains on foot is 100% unrestricted.
        int ceiling = item.getServiceCeiling();
        if (isFlying && !player.onGround() && player.getY() >= ceiling) {
            Vec3 vel = player.getDeltaMovement();
            if (vel.y > 0) {
                // Heavily dampen upward climb rate in thin air above ceiling
                player.setDeltaMovement(new Vec3(vel.x * 0.90, Math.min(vel.y * 0.20, 0.035), vel.z * 0.90));
            }
            // Core strain: Engines overheat much faster when forced above ceiling
            data.heat = Math.min(100.0F, data.heat + 0.85F * item.getHeatGainMult());

            if (player.tickCount % 30 == 0) {
                player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.CAMPFIRE_CRACKLE, SoundSource.PLAYERS, 0.6F, 1.6F);
                player.displayClientMessage(Component.translatable("message.youjosenki.ceiling_strained", unitName, ceiling), true);
            }
        }

        // 2. Heat & Cooling Management
        if (isFlying) {
            if (data.overheated) {
                // Emergency cooling phase: boost locked out
                data.heat = Math.max(0.0F, data.heat - (0.65F * item.getCoolingRate()));
                // Vent steam particles
                if (player.level() instanceof ServerLevel serverLevel && player.tickCount % 2 == 0) {
                    serverLevel.sendParticles(ParticleTypes.CLOUD, player.getX(), player.getY() + 0.6, player.getZ(), 2, 0.15, 0.15, 0.15, 0.02);
                    serverLevel.sendParticles(ParticleTypes.SMOKE, player.getX(), player.getY() + 0.6, player.getZ(), 1, 0.1, 0.1, 0.1, 0.01);
                }
                if (data.heat <= 30.0F) {
                    data.overheated = false;
                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.EXPERIENCE_ORB_PICKUP, SoundSource.PLAYERS, 0.8F, 1.4F);
                    player.displayClientMessage(Component.translatable("message.youjosenki.cooled_down", unitName), true);
                }
            } else {
                if (isSprinting) {
                    data.heat = Math.min(100.0F, data.heat + 0.25F * item.getHeatGainMult());
                } else {
                    data.heat = Math.max(0.0F, data.heat - (0.45F * item.getCoolingRate()));
                }

                if (data.heat >= 100.0F) {
                    data.overheated = true;
                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.FIRE_EXTINGUISH, SoundSource.PLAYERS, 1.0F, 0.85F);
                    player.displayClientMessage(Component.translatable("message.youjosenki.overheat", unitName), true);
                }
            }
        } else {
            // Ground cooling
            data.heat = Math.max(0.0F, data.heat - (0.8F * item.getCoolingRate()));
            if (data.heat <= 30.0F) {
                data.overheated = false;
            }
        }

        // Water immersion rapid cooling: if submerged in water, dissipate heat 4x faster!
        if (player.isInWater()) {
            data.heat = Math.max(0.0F, data.heat - 3.5F);
            if (data.heat <= 30.0F && data.overheated) {
                data.overheated = false;
                player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.FIRE_EXTINGUISH, SoundSource.PLAYERS, 0.8F, 1.2F);
                player.displayClientMessage(Component.translatable("message.youjosenki.cooled_down", unitName), true);
            }
        }

        // Reset boost step if inactive for 2 seconds
        if (player.level().getGameTime() - data.lastBoostTime > 40) {
            data.boostStep = 1;
        }

        if (data.boostCooldown > 0) {
            data.boostCooldown--;
        }

        // Sync telemetry to client periodically
        if (player.tickCount % 6 == 0) {
            ModNetworking.sendToPlayer(new SyncFlightTelemetryS2CPacket(data.heat, data.overheated, ceiling, data.boostStep), player);
        }
    }

    public static void handlePlayerBoost(ServerPlayer player) {
        ItemStack unit = EleniumFlightUnitItem.getEquippedFlightUnit(player);
        if (unit == null || !EleniumFlightUnitItem.isItemEnergized(unit)) return;
        if (!(unit.getItem() instanceof EleniumFlightUnitItem item)) return;

        // Disallow boost in water for non-waterproof models
        if (!item.isWaterproof() && player.isInWater()) {
            player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.GENERIC_EXTINGUISH_FIRE, SoundSource.PLAYERS, 0.8F, 1.3F);
            player.displayClientMessage(Component.translatable("message.youjosenki.water_stall", unit.getHoverName().getString()), true);
            return;
        }

        PlayerFlightData data = getPlayerData(player.getUUID());
        if (data.overheated || data.boostCooldown > 0) return;

        long now = player.level().getGameTime();
        if (now - data.lastBoostTime < 35) {
            data.boostStep = Math.min(3, data.boostStep + 1);
        } else {
            data.boostStep = 1;
        }
        data.lastBoostTime = now;

        // Progressive Energy Drain: Higher/consecutive boost steps consume significantly more energy
        // Step 1 = 1.0x (180 FE), Step 2 = 2.2x (396 FE), Step 3 = 4.0x (720 FE)
        int baseBoostCost = Config.COMMON.sprintEnergyCost.get() * 3;
        float drainMultiplier = 1.0F + (data.boostStep - 1) * 1.5F;
        int boostCost = (int) (baseBoostCost * drainMultiplier * item.getEnergyDrainMult());

        IEnergyStorage energy = unit.getCapability(ForgeCapabilities.ENERGY).orElse(null);
        if (energy != null && energy.getEnergyStored() < boostCost) {
            player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.EXPERIENCE_ORB_PICKUP, SoundSource.PLAYERS, 0.5F, 0.6F);
            player.displayClientMessage(Component.translatable("message.youjosenki.no_energy", unit.getHoverName().getString()), true);
            return;
        }
        if (energy != null) energy.extractEnergy(boostCost, false);

        // Heat accumulation: +20% for step 1, +26% for step 2, +34% for step 3
        float heatGain = (20.0F + (data.boostStep - 1) * 7.0F) * item.getHeatGainMult();
        data.heat = Math.min(100.0F, data.heat + heatGain);
        data.boostCooldown = item.getBoostCooldownTicks();

        float stepMult = 1.0F + (data.boostStep - 1) * 0.20F;
        float finalBoostPower = 0.22F * item.getBoostMultiplier() * stepMult;

        Vec3 look = player.getLookAngle();
        Vec3 addedVel = look.scale(finalBoostPower);
        if (!player.onGround() && player.getY() >= item.getServiceCeiling() && addedVel.y > 0) {
            addedVel = new Vec3(addedVel.x, Math.min(addedVel.y * 0.15, 0.02), addedVel.z);
        }
        Vec3 currentVel = player.getDeltaMovement();
        Vec3 newVel = currentVel.scale(0.85).add(addedVel);
        double spd = newVel.length();
        if (spd > 1.40) {
            newVel = newVel.scale(1.40 / spd);
        }
        player.setDeltaMovement(newVel);
        player.hurtMarked = true;

        if (player.level() instanceof ServerLevel serverLevel) {
            FlightVFXHelper.spawnShockwaveRing(serverLevel, player, item.getSoundProfile(), data.boostStep);
        }

        ModNetworking.sendToPlayer(new SyncFlightTelemetryS2CPacket(data.heat, data.overheated, item.getServiceCeiling(), data.boostStep), player);
    }
}
