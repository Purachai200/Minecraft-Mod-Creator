package com.titancombat.entity.transport;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;

/** Water-only hull with a walkable deck: the patrol boat and the frigate differ only in numbers, so they share this. */
public abstract class BaseShipEntity extends BaseTransportVehicleEntity {
    protected BaseShipEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(0.6F);
    }

    /** Animation / model key, e.g. "patrol_boat". */
    protected abstract String key();

    protected abstract float maxForward();

    protected abstract float acceleration();

    protected abstract float turnRate();

    /** Fluid depth (blocks) the hull settles at. */
    protected abstract double waterline();

    /** Stern wake distance behind the origin, blocks. */
    protected abstract double sternDistance();

    @Override
    public void tick() {
        super.tick();
        if (this.isInWater()) {
            double fluidHeight = this.getFluidHeight(FluidTags.WATER);
            if (fluidHeight > 0.0D) {
                Vec3 m = this.getDeltaMovement();
                this.setDeltaMovement(m.x, m.y * 0.78D + (fluidHeight - waterline()) * 0.15D, m.z);
            }
        }
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        if (!this.isInWater() && this.onGround()) { // beached
            this.currentSpeed = approach(this.currentSpeed, 0.0F, 0.05F);
            moveAlongHeading(1.0F, gravityMotion());
            if (driver instanceof Player p && this.tickCount % 40 == 0 && !this.level().isClientSide) {
                p.displayClientMessage(Component.literal("§c[NAVAL WARNING] Hull is aground! Water required to navigate."), true);
            }
            return;
        }
        updateThrottle(driver, maxForward(), maxForward() * 0.35F, acceleration(), acceleration() * 1.6F, acceleration() * 0.35F);
        float steer = Math.abs(this.currentSpeed) < 0.05F ? 0.4F : Math.signum(this.currentSpeed);
        this.yawDelta = Math.abs(driver.xxa) > 0.01F ? -driver.xxa * steer * turnRate() : 0.0F;
        moveAlongHeading(1.0F, gravityMotion());

        if (this.level().isClientSide && Math.abs(this.currentSpeed) > 0.08F && this.isInWater()) {
            double yawRad = Math.toRadians(this.getYRot());
            double sx = this.getX() + Math.sin(yawRad) * sternDistance(), sz = this.getZ() - Math.cos(yawRad) * sternDistance();
            for (int i = 0; i < 2; i++) {
                this.level().addParticle(ParticleTypes.SPLASH, sx + (this.random.nextDouble() - 0.5D) * 2.0D, this.getY() + 0.3D,
                        sz + (this.random.nextDouble() - 0.5D) * 2.0D, -Math.sin(yawRad) * 0.3D, 0.15D, Math.cos(yawRad) * 0.3D);
            }
        }
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "sail", 4, event -> event.setAndContinue(RawAnimation.begin().thenLoop(
                "animation." + key() + (Math.abs(this.visSpeed) > 0.03F ? ".sail" : ".idle")))));
    }
}
