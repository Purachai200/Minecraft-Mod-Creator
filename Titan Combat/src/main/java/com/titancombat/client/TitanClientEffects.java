package com.titancombat.client;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanClass;
import com.titancombat.sound.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * Client-only titan feedback: footsteps (driven by animation sound keyframes so they land with the
 * feet), ground dust, muzzle flash, thruster bursts and cockpit shake. Called from entity events and
 * GeckoLib keyframe handlers, which only ever run on the client.
 */
public final class TitanClientEffects {
    private TitanClientEffects() {}

    public static void onSoundKeyframe(BaseTitanEntity titan, String effect) {
        if (effect == null || !effect.contains("step")) return;
        Level level = titan.level();
        if (!level.isClientSide || !titan.onGround()) return;

        boolean run = effect.startsWith("run_");
        boolean left = effect.endsWith("left");
        TitanClass c = titan.getTitanClass();

        // Foot sits roughly a block to the side of the hips and a little ahead when it lands.
        float yawRad = titan.yBodyRot * ((float) Math.PI / 180.0F);
        double side = left ? 1.0D : -1.0D;
        double fx = -Math.sin(yawRad), fz = Math.cos(yawRad);
        double rx = -Math.cos(yawRad), rz = -Math.sin(yawRad);
        double footX = titan.getX() + rx * side * 1.1D + fx * 0.6D;
        double footZ = titan.getZ() + rz * side * 1.1D + fz * 0.6D;
        double footY = titan.getY();

        float weight = weightOf(c);
        float volume = (run ? 2.0F : 1.6F) * weight;
        float pitch = (1.12F - 0.25F * weight) + titan.getRandom().nextFloat() * 0.1F;
        level.playLocalSound(footX, footY, footZ, ModSounds.TITAN_STEP.get(), SoundSource.NEUTRAL, volume, pitch, false);

        // Kick up the ground the foot hit.
        BlockState ground = level.getBlockState(BlockPos.containing(footX, footY - 0.2D, footZ));
        RandomSource r = titan.getRandom();
        if (ground.getRenderShape() != RenderShape.INVISIBLE) {
            int count = run ? 14 : 8;
            for (int i = 0; i < count; i++) {
                level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK, ground),
                        footX + (r.nextDouble() - 0.5D) * 1.4D, footY + 0.1D, footZ + (r.nextDouble() - 0.5D) * 1.4D,
                        (r.nextDouble() - 0.5D) * 0.3D, 0.15D + r.nextDouble() * 0.2D, (r.nextDouble() - 0.5D) * 0.3D);
            }
        }
        if (run) {
            level.addParticle(ParticleTypes.POOF, footX, footY + 0.2D, footZ, 0, 0.02D, 0);
        }

        float base = (run ? 0.32F : 0.22F) * weight;
        shakeNearby(titan, base, 18.0D);
    }

    /** Howitzer shot: muzzle flash and a cloud of smoke around the back mount, and a camera kick for the pilot. */
    public static void onHowitzerFired(BaseTitanEntity titan) {
        Level level = titan.level();
        RandomSource r = titan.getRandom();
        Vec3 m = titan.getArtilleryMuzzle();
        level.addParticle(ParticleTypes.FLASH, m.x, m.y + 1.0D, m.z, 0, 0, 0);
        for (int i = 0; i < 14; i++) {
            level.addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE, m.x, m.y, m.z,
                    (r.nextDouble() - 0.5D) * 0.15D, 0.05D + r.nextDouble() * 0.08D, (r.nextDouble() - 0.5D) * 0.15D);
        }
        if (isPilot(titan)) CockpitCamera.addRecoil(3.0F);
    }

    public static void onEntityEvent(BaseTitanEntity titan, byte id) {
        Level level = titan.level();
        RandomSource r = titan.getRandom();
        switch (id) {
            case BaseTitanEntity.EVENT_WEAPON_FIRE -> {
                Vec3 m = titan.getMuzzlePosition();
                level.addParticle(ParticleTypes.FLASH, m.x, m.y, m.z, 0, 0, 0);
                for (int i = 0; i < 4; i++) {
                    level.addParticle(ParticleTypes.SMOKE, m.x, m.y, m.z,
                            (r.nextDouble() - 0.5D) * 0.08D, 0.04D, (r.nextDouble() - 0.5D) * 0.08D);
                }
                if (isPilot(titan)) {
                    CockpitCamera.addRecoil(recoilOf(titan.getTitanClass()));
                }
            }
            case BaseTitanEntity.EVENT_DASH -> {
                float yawRad = titan.yBodyRot * ((float) Math.PI / 180.0F);
                double bx = Math.sin(yawRad), bz = -Math.cos(yawRad); // behind the titan
                for (int i = 0; i < 24; i++) {
                    double spread = (r.nextDouble() - 0.5D) * 1.6D;
                    level.addParticle(i % 3 == 0 ? ParticleTypes.FLAME : ParticleTypes.CLOUD,
                            titan.getX() + bx * 1.2D + bz * spread, titan.getY() + 3.6D + r.nextDouble(), titan.getZ() + bz * 1.2D - bx * spread,
                            bx * 0.35D, -0.05D, bz * 0.35D);
                }
                if (isPilot(titan)) CockpitCamera.addTrauma(0.35F);
            }
            case BaseTitanEntity.EVENT_MELEE_SWING -> {
                if (isPilot(titan)) CockpitCamera.addTrauma(0.12F);
            }
            case BaseTitanEntity.EVENT_MELEE_IMPACT -> {
                float yawRad = titan.yBodyRot * ((float) Math.PI / 180.0F);
                double x = titan.getX() - Math.sin(yawRad) * 3.5D, z = titan.getZ() + Math.cos(yawRad) * 3.5D;
                for (int i = 0; i < 16; i++) {
                    level.addParticle(ParticleTypes.CRIT, x, titan.getY() + 2.5D + r.nextDouble(), z,
                            (r.nextDouble() - 0.5D), r.nextDouble() * 0.5D, (r.nextDouble() - 0.5D));
                }
                level.addParticle(ParticleTypes.EXPLOSION, x, titan.getY() + 3.0D, z, 0, 0, 0);
                shakeNearby(titan, 0.7F, 10.0D);
            }
            case BaseTitanEntity.EVENT_JUMP -> {
                for (int i = 0; i < 30; i++) {
                    double a = r.nextDouble() * Math.PI * 2.0D;
                    level.addParticle(i % 4 == 0 ? ParticleTypes.FLAME : ParticleTypes.CLOUD,
                            titan.getX() + Math.cos(a) * 1.2D, titan.getY() + 0.3D, titan.getZ() + Math.sin(a) * 1.2D,
                            Math.cos(a) * 0.35D, 0.02D, Math.sin(a) * 0.35D);
                }
                if (isPilot(titan)) CockpitCamera.addTrauma(0.3F);
            }
            case BaseTitanEntity.EVENT_EJECT -> {
                // Hatch blow-out: a burst of flame and smoke from the cockpit.
                double y = titan.getY() + titan.getTitanClass().getCockpitEyeY(titan.isKneeling());
                for (int i = 0; i < 30; i++) {
                    level.addParticle(i % 2 == 0 ? ParticleTypes.FLAME : ParticleTypes.LARGE_SMOKE,
                            titan.getX(), y, titan.getZ(), (r.nextDouble() - 0.5D) * 0.5D, 0.3D + r.nextDouble() * 0.4D, (r.nextDouble() - 0.5D) * 0.5D);
                }
                level.addParticle(ParticleTypes.EXPLOSION, titan.getX(), y, titan.getZ(), 0, 0, 0);
                CockpitCamera.addTrauma(0.8F);
                if (isPilot(titan)) {
                    // Player movement is client-side: the ejection seat's kick has to be applied here.
                    float yawRad = titan.getYRot() * ((float) Math.PI / 180.0F);
                    com.titancombat.client.cockpit.CockpitState.queueEjectLaunch(-Math.sin(yawRad) * 0.6D, 2.4D, Math.cos(yawRad) * 0.6D);
                }
            }
            case BaseTitanEntity.EVENT_EMBARK -> {
                if (isPilot(titan)) CockpitCamera.addTrauma(0.2F);
            }
            default -> {}
        }
    }

    /** Per-tick jet exhaust: rear thrusters while dashing/sprinting, downward jets while airborne. */
    public static void thrusterTick(BaseTitanEntity titan, boolean dashing, boolean airborne, boolean sprinting) {
        Level level = titan.level();
        RandomSource r = titan.getRandom();
        float yawRad = titan.getYRot() * ((float) Math.PI / 180.0F);
        double bx = Math.sin(yawRad), bz = -Math.cos(yawRad);  // backwards
        double rx = -Math.cos(yawRad), rz = -Math.sin(yawRad); // right
        double backY = titan.getY() + (titan.isKneeling() ? 2.6D : 4.0D);

        if (dashing) {
            for (int side = -1; side <= 1; side += 2) {
                double x = titan.getX() + bx * 1.3D + rx * side * 0.7D;
                double z = titan.getZ() + bz * 1.3D + rz * side * 0.7D;
                for (int i = 0; i < 2; i++) {
                    level.addParticle(ParticleTypes.FLAME, x, backY, z,
                            bx * 0.45D + (r.nextDouble() - 0.5D) * 0.08D, -0.02D, bz * 0.45D + (r.nextDouble() - 0.5D) * 0.08D);
                }
                level.addParticle(ParticleTypes.SOUL_FIRE_FLAME, x, backY, z, bx * 0.25D, 0, bz * 0.25D);
                level.addParticle(ParticleTypes.LARGE_SMOKE, x + bx * 0.6D, backY, z + bz * 0.6D, bx * 0.1D, 0.02D, bz * 0.1D);
            }
        }
        if (airborne) {
            for (int side = -1; side <= 1; side += 2) {
                double x = titan.getX() + bx * 0.9D + rx * side * 0.6D;
                double z = titan.getZ() + bz * 0.9D + rz * side * 0.6D;
                level.addParticle(ParticleTypes.FLAME, x, backY - 0.4D, z, (r.nextDouble() - 0.5D) * 0.05D, -0.5D, (r.nextDouble() - 0.5D) * 0.05D);
                level.addParticle(ParticleTypes.SOUL_FIRE_FLAME, x, backY - 0.5D, z, 0, -0.35D, 0);
                if (r.nextInt(3) == 0) {
                    level.addParticle(ParticleTypes.CLOUD, x, backY - 1.0D, z, 0, -0.2D, 0);
                }
            }
        }
        if (sprinting && !dashing && titan.tickCount % 3 == 0) {
            double x = titan.getX() + bx * 1.2D, z = titan.getZ() + bz * 1.2D;
            level.addParticle(ParticleTypes.SMOKE, x + rx * 0.6D, backY + 0.3D, z + rz * 0.6D, bx * 0.05D, 0.05D, bz * 0.05D);
            level.addParticle(ParticleTypes.SMOKE, x - rx * 0.6D, backY + 0.3D, z - rz * 0.6D, bx * 0.05D, 0.05D, bz * 0.05D);
        }
    }

    /** Heavy touchdown after a jump or drop: dust ring, stomp, shake. */
    public static void onLanding(BaseTitanEntity titan, float strength) {
        Level level = titan.level();
        RandomSource r = titan.getRandom();
        BlockState ground = level.getBlockState(titan.blockPosition().below());
        for (int i = 0; i < 40; i++) {
            double a = r.nextDouble() * Math.PI * 2.0D;
            double d = 1.0D + r.nextDouble() * 1.5D;
            double x = titan.getX() + Math.cos(a) * d, z = titan.getZ() + Math.sin(a) * d;
            if (ground.getRenderShape() != RenderShape.INVISIBLE && i % 2 == 0) {
                level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK, ground), x, titan.getY() + 0.1D, z,
                        Math.cos(a) * 0.4D, 0.2D, Math.sin(a) * 0.4D);
            } else {
                level.addParticle(ParticleTypes.POOF, x, titan.getY() + 0.2D, z, Math.cos(a) * 0.25D, 0.02D, Math.sin(a) * 0.25D);
            }
        }
        level.playLocalSound(titan.getX(), titan.getY(), titan.getZ(), ModSounds.TITAN_STEP.get(), SoundSource.NEUTRAL, 2.5F, 0.6F, false);
        level.playLocalSound(titan.getX(), titan.getY(), titan.getZ(), net.minecraft.sounds.SoundEvents.ANVIL_LAND, SoundSource.NEUTRAL, 0.6F, 0.5F, false);
        shakeNearby(titan, 0.35F + 0.5F * strength, 20.0D);
    }

    private static void shakeNearby(BaseTitanEntity titan, float strength, double radius) {
        Player player = Minecraft.getInstance().player;
        if (player == null) return;
        if (player.getVehicle() == titan) {
            CockpitCamera.addTrauma(strength);
            return;
        }
        double d = player.distanceTo(titan);
        if (d < radius) {
            CockpitCamera.addTrauma(strength * 0.6F * (float) (1.0D - d / radius));
        }
    }

    private static boolean isPilot(BaseTitanEntity titan) {
        Player player = Minecraft.getInstance().player;
        return player != null && player.getVehicle() == titan;
    }

    /** Heavier chassis hit the ground harder. */
    private static float weightOf(TitanClass c) {
        return switch (c) {
            case LEGION -> 1.25F;
            case SCORCH -> 1.15F;
            case RONIN, NORTHSTAR -> 0.85F;
            default -> 1.0F;
        };
    }

    private static float recoilOf(TitanClass c) {
        return switch (c) {
            case NORTHSTAR -> 1.6F;
            case TONE, SCORCH -> 1.1F;
            case RONIN -> 1.3F;
            case LEGION -> 0.25F;
            case MONARCH -> 0.35F;
            default -> 0.6F;
        };
    }
}
