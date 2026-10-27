package com.titancombat.util;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.UUID;

public class TitanWarpHelper {

    /** Maximum tactical recall communication range in blocks (250m). */
    public static final double MAX_RECALL_RANGE = 250.0D;

    @Nullable
    public static BaseTitanEntity findCurrentTitanOfPlayer(@Nullable MinecraftServer server, @Nullable Player player) {
        if (server == null || player == null) return null;
        String playerUUID = player.getUUID().toString();
        for (ServerLevel level : server.getAllLevels()) {
            for (Entity entity : level.getAllEntities()) {
                if (entity instanceof BaseTitanEntity titan && titan.isAlive()) {
                    if (playerUUID.equals(titan.getOwnerUUID())) {
                        return titan;
                    }
                }
            }
        }
        return null;
    }

    @Nullable
    public static BaseTitanEntity findTitan(MinecraftServer server, @Nullable UUID titanUUID, @Nullable Player owner, @Nullable String dimensionId, long lastPosLong) {
        // STRICT: Must have a valid TitanUUID bound to this specific device!
        // No fallback to any random titan so devices only control their explicitly paired Mech.
        if (titanUUID == null) {
            return null;
        }

        // 1. Search all currently loaded entities across all dimensions
        for (ServerLevel level : server.getAllLevels()) {
            Entity e = level.getEntity(titanUUID);
            if (e instanceof BaseTitanEntity titan) {
                if (owner != null && titan.getOwnerUUID() != null && !titan.getOwnerUUID().isEmpty()
                        && !owner.getUUID().toString().equals(titan.getOwnerUUID())) {
                    return null; // Not owner
                }
                return titan;
            }
        }

        // 2. If chunk is unloaded, try to force-load the chunk from last known position/dimension
        if (dimensionId != null && !dimensionId.isEmpty() && lastPosLong != 0) {
            ResourceLocation dimLoc = ResourceLocation.tryParse(dimensionId);
            if (dimLoc != null) {
                ResourceKey<Level> dimKey = ResourceKey.create(Registries.DIMENSION, dimLoc);
                ServerLevel sLevel = server.getLevel(dimKey);
                if (sLevel != null) {
                    BlockPos lastPos = BlockPos.of(lastPosLong);
                    ChunkPos cPos = new ChunkPos(lastPos);
                    sLevel.getChunkSource().addRegionTicket(TicketType.PORTAL, cPos, 2, lastPos);
                    Entity e = sLevel.getEntity(titanUUID);
                    if (e instanceof BaseTitanEntity titan) {
                        if (owner != null && titan.getOwnerUUID() != null && !titan.getOwnerUUID().isEmpty()
                                && !owner.getUUID().toString().equals(titan.getOwnerUUID())) {
                            return null;
                        }
                        return titan;
                    }
                }
            }
        }

        return null;
    }

    public static boolean warpTitanTo(BaseTitanEntity titan, ServerLevel targetLevel, Vec3 targetPos, float yaw, Player pilot) {
        // Validation: Ownership check - only the registered pilot can recall this Titan
        if (titan.getOwnerUUID() != null && !titan.getOwnerUUID().isEmpty()
                && !pilot.getUUID().toString().equals(titan.getOwnerUUID())) {
            pilot.sendSystemMessage(Component.translatable("message.titancombat.access_denied", titan.getOwnerName()));
            pilot.level().playSound(null, pilot.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.2F);
            return false;
        }

        // Validation: cannot warp if another player is piloting
        if (titan.isVehicle()) {
            Entity rider = titan.getFirstPassenger();
            if (rider != null && rider != pilot) {
                pilot.sendSystemMessage(Component.literal("§c[WARP ERROR] Titan is currently occupied by pilot: " + rider.getName().getString()));
                return false;
            }
        }

        // Validation: Dimension check - cannot recall across different dimensions
        if (titan.level().dimension() != targetLevel.dimension()) {
            pilot.sendSystemMessage(Component.translatable("message.titancombat.warp_dimension_error"));
            pilot.level().playSound(null, pilot.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.2F);
            return false;
        }

        // Validation: Distance check - within MAX_RECALL_RANGE
        double distance = titan.position().distanceTo(targetPos);
        if (distance > MAX_RECALL_RANGE) {
            pilot.sendSystemMessage(Component.translatable("message.titancombat.warp_out_of_range", (int) distance, (int) MAX_RECALL_RANGE));
            pilot.level().playSound(null, pilot.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.2F);
            return false;
        }

        // Clean vehicle dismount if Titan is loaded on a transport vehicle (Truck, Skycrane Drone, Cargo Barge)
        if (titan.isPassenger()) {
            Entity vehicle = titan.getVehicle();
            titan.stopRiding();
            if (vehicle instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity transport) {
                boolean hasRemainingCargo = false;
                for (Entity p : transport.getPassengers()) {
                    if (p instanceof BaseTitanEntity) {
                        hasRemainingCargo = true;
                        break;
                    }
                }
                transport.setHasCargo(hasRemainingCargo);
            }
        }

        // 1. Departure VFX & Sound at old position
        ServerLevel oldLevel = (ServerLevel) titan.level();
        Vec3 oldPos = titan.position();
        oldLevel.sendParticles(ParticleTypes.PORTAL, oldPos.x, oldPos.y + 2.0D, oldPos.z, 60, 1.5D, 2.0D, 1.5D, 0.2D);
        oldLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, oldPos.x, oldPos.y + 2.0D, oldPos.z, 40, 1.2D, 1.8D, 1.2D, 0.3D);
        oldLevel.playSound(null, oldPos.x, oldPos.y, oldPos.z, SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 2.0F, 0.8F);
        oldLevel.playSound(null, oldPos.x, oldPos.y, oldPos.z, SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 2.0F, 1.2F);

        // 2. Change dimension if necessary
        if (oldLevel != targetLevel) {
            titan.changeDimension(targetLevel);
        }

        // 3. Relocate to target position
        titan.moveTo(targetPos.x, targetPos.y, targetPos.z, yaw, 0.0F);
        titan.teleportTo(targetPos.x, targetPos.y, targetPos.z);
        titan.setDeltaMovement(0, 0, 0);
        titan.fallDistance = 0.0F;
        titan.setStandbyMode(false);
        titan.setSitting(false);
        titan.getNavigation().stop();

        // 4. Blue Barrier Dome & Overshield (Surrounded by glowing blue energy dome for 12s)
        titan.setShield(titan.getMaxShield());
        titan.setWarpDefenseTicks(240); // 12 seconds of full blue dome shield & invulnerability

        // 5. Arrival VFX & SFX at destination
        targetLevel.sendParticles(ParticleTypes.FLASH, targetPos.x, targetPos.y + 2.5D, targetPos.z, 3, 0.5D, 0.5D, 0.5D, 0.0D);
        targetLevel.sendParticles(ParticleTypes.SONIC_BOOM, targetPos.x, targetPos.y + 1.8D, targetPos.z, 1, 0, 0, 0, 0);
        targetLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, targetPos.x, targetPos.y + 2.0D, targetPos.z, 100, 2.0D, 2.5D, 2.0D, 0.25D);
        targetLevel.sendParticles(ParticleTypes.PORTAL, targetPos.x, targetPos.y + 2.0D, targetPos.z, 120, 2.5D, 2.5D, 2.5D, 0.4D);

        targetLevel.playSound(null, targetPos.x, targetPos.y, targetPos.z, SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 2.5F, 1.2F);
        targetLevel.playSound(null, targetPos.x, targetPos.y, targetPos.z, SoundEvents.WARDEN_SONIC_BOOM, SoundSource.PLAYERS, 1.8F, 1.5F);
        targetLevel.playSound(null, targetPos.x, targetPos.y, targetPos.z, SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 2.0F, 0.8F);
        targetLevel.playSound(null, targetPos.x, targetPos.y, targetPos.z, com.titancombat.sound.ModSounds.TITAN_CABIN_ENTER.get(), SoundSource.PLAYERS, 2.0F, 1.0F);

        pilot.sendSystemMessage(Component.translatable("message.titancombat.warp_inbound", titan.getTitanClass().getDisplayName()));
        return true;
    }
}
