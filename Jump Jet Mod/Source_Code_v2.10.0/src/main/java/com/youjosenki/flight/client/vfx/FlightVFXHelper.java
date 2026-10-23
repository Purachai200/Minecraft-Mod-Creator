package com.youjosenki.flight.client.vfx;

import com.youjosenki.flight.sound.FlightSoundProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

public class FlightVFXHelper {

    /**
     * Spawns an expanding 3D sonic Mach shockwave ring behind the player.
     * High-tech units emit green/cyan acoustic energy rings (Warden-style).
     * Vintage units emit white vapor Mach cone condensation rings.
     */
    public static void spawnShockwaveRing(ServerLevel serverLevel, Player player, FlightSoundProfile soundProfile) {
        Vec3 look = player.getLookAngle().normalize();
        Vec3 nozzlePos = player.position().add(0, 0.65, 0).subtract(look.scale(0.85));

        // Orthonormal basis perpendicular to flight direction
        Vec3 up = Math.abs(look.y) > 0.85 ? new Vec3(1, 0, 0) : new Vec3(0, 1, 0);
        Vec3 u = look.cross(up).normalize();
        Vec3 v = look.cross(u).normalize();

        boolean isHighTech = (soundProfile == FlightSoundProfile.PROTOTYPE_MANA_CORE ||
                              soundProfile == FlightSoundProfile.AERODYNAMIC_STREAM ||
                              soundProfile == FlightSoundProfile.MODERN_MILITARY_JET ||
                              soundProfile == FlightSoundProfile.STEALTH_RECON_WHISPER);

        double radius = 1.35;
        int ringParticles = 18;

        if (isHighTech) {
            // Sonic boom at nozzle center
            serverLevel.sendParticles(ParticleTypes.SONIC_BOOM, nozzlePos.x, nozzlePos.y, nozzlePos.z, 1, 0, 0, 0, 0);

            // Green/cyan acoustic mana shockwave ring (Warden style)
            for (int i = 0; i < ringParticles; i++) {
                double angle = (2.0 * Math.PI * i) / ringParticles;
                double cos = Math.cos(angle) * radius;
                double sin = Math.sin(angle) * radius;
                Vec3 pt = nozzlePos.add(u.scale(cos)).add(v.scale(sin));
                serverLevel.sendParticles(ParticleTypes.SCULK_CHARGE_POP, pt.x, pt.y, pt.z, 1, 0.02, 0.02, 0.02, 0.01);
                serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, pt.x, pt.y, pt.z, 1, 0.03, 0.03, 0.03, 0.02);
            }

            // Air-shattering sonic whip sound ("เสียงทะลุลม")
            serverLevel.playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.WARDEN_SONIC_BOOM, SoundSource.PLAYERS, 1.15F, 1.60F);
            serverLevel.playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.TRIDENT_RIPTIDE_3, SoundSource.PLAYERS, 1.25F, 1.35F);
        } else {
            // Vintage / Rocket: White vapor condensation Mach cone ring
            for (int i = 0; i < ringParticles; i++) {
                double angle = (2.0 * Math.PI * i) / ringParticles;
                double cos = Math.cos(angle) * radius;
                double sin = Math.sin(angle) * radius;
                Vec3 pt = nozzlePos.add(u.scale(cos)).add(v.scale(sin));
                serverLevel.sendParticles(ParticleTypes.CLOUD, pt.x, pt.y, pt.z, 1, 0.03, 0.03, 0.03, 0.02);
                serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, pt.x, pt.y, pt.z, 1, 0.01, 0.01, 0.01, 0.001);
                serverLevel.sendParticles(ParticleTypes.LARGE_SMOKE, pt.x, pt.y, pt.z, 1, 0.02, 0.02, 0.02, 0.01);
            }

            // Classic heavy explosion thrust sound
            serverLevel.playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.GENERIC_EXPLODE, SoundSource.PLAYERS, 0.85F, 1.85F);
            serverLevel.playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.FIREWORK_ROCKET_LARGE_BLAST, SoundSource.PLAYERS, 1.20F, 1.10F);
            serverLevel.playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.TRIDENT_RIPTIDE_1, SoundSource.PLAYERS, 1.00F, 1.10F);
        }
    }

    /**
     * Realistic Ground Downwash & Surface Wind Pressure:
     * When flying or hovering near the ground, engine exhaust creates turbulent downwash,
     * blowing radial wind cushions, kicking up actual ground debris/dust particles, water spray,
     * and atmospheric ground-effect pressure clouds.
     */
    public static void handleGroundDownwash(ServerLevel serverLevel, Player player, boolean isSprinting, boolean isMoving, FlightSoundProfile soundProfile) {
        double px = player.getX();
        double py = player.getY();
        double pz = player.getZ();

        BlockPos.MutableBlockPos mpos = new BlockPos.MutableBlockPos();
        double groundY = -1;
        BlockState groundState = null;
        boolean isWater = false;

        // Scan downwards up to 5.5 blocks
        for (double dy = 0.4; dy <= 5.5; dy += 0.4) {
            mpos.set(px, py - dy, pz);
            BlockState state = serverLevel.getBlockState(mpos);
            if (!state.isAir()) {
                if (!state.getFluidState().isEmpty()) {
                    groundY = mpos.getY() + 0.9;
                    groundState = state;
                    isWater = true;
                    break;
                } else if (!state.getCollisionShape(serverLevel, mpos).isEmpty()) {
                    groundY = mpos.getY() + 1.0;
                    groundState = state;
                    break;
                }
            }
        }

        if (groundState == null || groundY <= -64) {
            return;
        }

        double altitude = py - groundY;
        if (altitude < 0.2 || altitude > 5.2) {
            return;
        }

        // Intensity: from 1.0 at deck (<1.0m) down to 0.15 at 5m
        float intensity = (float) Math.max(0.15, (5.2 - altitude) / 5.0);

        // Throttle frequency for high performance
        if (player.tickCount % (isSprinting ? 1 : 2) != 0) {
            return;
        }

        int particleCount = isSprinting ? 6 : 4;
        double ringRadius = 0.7 + (1.0 - intensity * 0.4) * (isSprinting ? 1.4 : 0.9);
        double expansionSpeed = (0.12 + intensity * 0.22) * (isSprinting ? 1.4 : 1.0);

        for (int i = 0; i < particleCount; i++) {
            double angle = (2.0 * Math.PI * i) / particleCount + (player.tickCount * 0.45);
            double cos = Math.cos(angle);
            double sin = Math.sin(angle);
            double partX = px + cos * ringRadius;
            double partZ = pz + sin * ringRadius;
            double vx = cos * expansionSpeed;
            double vz = sin * expansionSpeed;
            double vy = 0.02 + intensity * 0.03;

            if (isWater) {
                serverLevel.sendParticles(ParticleTypes.SPLASH, partX, groundY + 0.05, partZ, 1, vx * 0.5, vy * 1.5, vz * 0.5, 0.06);
                serverLevel.sendParticles(ParticleTypes.CLOUD, partX, groundY + 0.05, partZ, 1, vx, 0.01, vz, 0.02);
            } else {
                // Real ground block debris dust (dirt, sand, stone, grass, etc.)
                serverLevel.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, groundState), partX, groundY + 0.05, partZ, 1, vx * 0.4, vy, vz * 0.4, 0.06);
                // Outward rushing aerodynamic wind cushion
                serverLevel.sendParticles(ParticleTypes.CLOUD, partX, groundY + 0.05, partZ, 1, vx * 0.8, 0.01, vz * 0.8, 0.01);
            }
        }

        // Low altitude wind rushing sound effect
        if (altitude < 2.5 && player.tickCount % 14 == 0) {
            if (isWater) {
                serverLevel.playSound(null, px, groundY, pz, SoundEvents.GENERIC_SWIM, SoundSource.PLAYERS, 0.35F * intensity, 1.3F);
            } else {
                serverLevel.playSound(null, px, groundY, pz, SoundEvents.ELYTRA_FLYING, SoundSource.PLAYERS, 0.30F * intensity, 1.5F);
            }
        }
    }
}
