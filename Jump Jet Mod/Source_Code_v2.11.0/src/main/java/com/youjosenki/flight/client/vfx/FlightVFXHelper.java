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
    public static void spawnShockwaveRing(ServerLevel serverLevel, Player player, FlightSoundProfile soundProfile, int boostStep) {
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

        // Vapour cone (Prandtl-Glauert): stacked condensation rings flaring out behind the wearer
        int rings = 2 + boostStep;
        for (int k = 0; k < rings; k++) {
            Vec3 c = nozzlePos.subtract(look.scale(0.4 + k * 0.55));
            double r = 0.45 + k * 0.32;
            int n = 10 + k * 4;
            for (int i = 0; i < n; i++) {
                double a = (2.0 * Math.PI * i) / n + k * 0.4;
                Vec3 radial = u.scale(Math.cos(a)).add(v.scale(Math.sin(a)));
                Vec3 pt = c.add(radial.scale(r));
                Vec3 vel = radial.scale(0.04).subtract(look.scale(0.06));
                serverLevel.sendParticles(ParticleTypes.CLOUD, pt.x, pt.y, pt.z, 0, vel.x, vel.y, vel.z, 1.0);
            }
        }
        if (boostStep >= 3) {
            serverLevel.sendParticles(ParticleTypes.FLASH, nozzlePos.x, nozzlePos.y, nozzlePos.z, 1, 0, 0, 0, 0);
            serverLevel.sendParticles(ParticleTypes.EXPLOSION, nozzlePos.x, nozzlePos.y, nozzlePos.z, 1, 0, 0, 0, 0);
        }

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
    public static void handleGroundDownwash(ServerLevel serverLevel, Player player, boolean isSprinting, boolean isMoving,
                                            FlightSoundProfile soundProfile, float thrust) {
        double px = player.getX();
        double py = player.getY();
        double pz = player.getZ();

        BlockPos.MutableBlockPos mpos = new BlockPos.MutableBlockPos();
        double groundY = -1;
        BlockState groundState = null;
        boolean isWater = false;

        double reach = 5.5 + thrust * 2.5; // heavy rigs blast the ground from higher up
        for (double dy = 0.4; dy <= reach; dy += 0.4) {
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
        double ceiling = reach - 0.3;
        if (altitude < 0.2 || altitude > ceiling) {
            return;
        }

        // Intensity: 1.0 at deck level falling to 0.15 at the edge of the rig's reach
        float intensity = (float) Math.max(0.15, (ceiling - altitude) / (ceiling - 0.2));

        // Throttle frequency for high performance
        if (player.tickCount % (isSprinting ? 1 : 2) != 0) {
            return;
        }

        int particleCount = Math.round((isSprinting ? 8 : 6) * (0.6F + thrust * 0.5F));
        double ringRadius = (0.7 + (1.0 - intensity * 0.4) * (isSprinting ? 1.4 : 0.9)) * (0.8 + thrust * 0.25);
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

        // Inner scouring ring kicked straight up under the nozzles
        if (!isWater && intensity > 0.5) {
            for (int i = 0; i < 3; i++) {
                double a = serverLevel.random.nextDouble() * Math.PI * 2;
                double r = serverLevel.random.nextDouble() * 0.6;
                serverLevel.sendParticles(ParticleTypes.POOF, px + Math.cos(a) * r, groundY + 0.1, pz + Math.sin(a) * r,
                        1, 0.05, 0.02, 0.05, 0.03 * thrust);
            }
        }

        // Rotor-wash pressure: shove loose items, mobs and other players away from the landing zone
        double pushRadius = 1.5 + thrust * 1.8 * intensity;
        net.minecraft.world.phys.AABB zone = new net.minecraft.world.phys.AABB(px - pushRadius, groundY - 0.5, pz - pushRadius,
                px + pushRadius, groundY + 2.5, pz + pushRadius);
        for (net.minecraft.world.entity.Entity e : serverLevel.getEntities(player, zone,
                e -> !e.isSpectator() && !e.isPassenger() && (e instanceof net.minecraft.world.entity.item.ItemEntity
                        || e instanceof net.minecraft.world.entity.ExperienceOrb || e.isPushable()))) {
            double ox = e.getX() - px, oz = e.getZ() - pz;
            double d = Math.sqrt(ox * ox + oz * oz);
            if (d < 0.05 || d > pushRadius) continue;
            double f = 0.05 * thrust * intensity * (1.0 - d / pushRadius);
            e.push(ox / d * f, 0.0, oz / d * f);
            e.hurtMarked = true;
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

    /**
     * Touchdown: expanding debris rings, a dust skirt, an impact thud scaled to the rig's mass,
     * and a short outward shove for anything standing too close. No block or entity damage.
     */
    public static void spawnLandingShockwave(ServerLevel serverLevel, Player player, float thrust) {
        BlockPos below = player.blockPosition().below();
        BlockState ground = serverLevel.getBlockState(below);
        double px = player.getX(), py = player.getY() + 0.05, pz = player.getZ();
        for (int ring = 0; ring < 3; ring++) {
            double r = 0.5 + ring * 0.6 * thrust;
            int n = 12 + ring * 6;
            double speed = 0.12 + 0.08 * thrust;
            for (int i = 0; i < n; i++) {
                double a = (2.0 * Math.PI * i) / n + ring * 0.3;
                double cx = Math.cos(a), cz = Math.sin(a);
                if (!ground.isAir()) {
                    serverLevel.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground),
                            px + cx * r, py, pz + cz * r, 0, cx * speed, 0.15, cz * speed, 1.0);
                }
                serverLevel.sendParticles(ParticleTypes.CLOUD, px + cx * r, py, pz + cz * r, 0, cx * speed * 0.8, 0.01, cz * speed * 0.8, 1.0);
            }
        }
        serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, px, py, pz, Math.round(4 * thrust), 0.6, 0.05, 0.6, 0.01);
        if (thrust >= 1.5) {
            serverLevel.sendParticles(ParticleTypes.EXPLOSION, px, py + 0.2, pz, 1, 0, 0, 0, 0);
            serverLevel.playSound(null, px, py, pz, SoundEvents.GENERIC_EXPLODE, SoundSource.PLAYERS, 0.45F, 1.5F);
        }
        serverLevel.playSound(null, px, py, pz, SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 0.25F * thrust, 1.7F / thrust);
        serverLevel.playSound(null, px, py, pz, SoundEvents.PISTON_CONTRACT, SoundSource.PLAYERS, 0.6F, 0.7F);

        double radius = 1.2 + thrust * 1.3;
        net.minecraft.world.phys.AABB zone = player.getBoundingBox().inflate(radius, 0.5, radius);
        for (net.minecraft.world.entity.Entity e : serverLevel.getEntities(player, zone, e -> !e.isSpectator() && !e.isPassenger())) {
            double ox = e.getX() - px, oz = e.getZ() - pz;
            double d = Math.sqrt(ox * ox + oz * oz);
            if (d < 0.05 || d > radius) continue;
            double f = 0.35 * thrust * (1.0 - d / radius);
            e.push(ox / d * f, 0.12 * thrust, oz / d * f);
            e.hurtMarked = true;
        }
    }
}
