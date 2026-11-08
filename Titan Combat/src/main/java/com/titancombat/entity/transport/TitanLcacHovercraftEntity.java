package com.titancombat.entity.transport;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;

/**
 * LCAC air-cushion landing craft: rides a skirt of air over water and beach alike, so it is the ship-to-shore link.
 * Low grip in turns (it slides like a hovercraft) and carries two Titans / Exoframes on its open deck.
 */
public class TitanLcacHovercraftEntity extends BaseTransportVehicleEntity {
    // Offsets in blocks (+X left, +Z forward); set from the model generator's report
    private static final Vec3 DRIVER_OFFSET = new Vec3(-2.75D, 3.5D - 0.6D, 3.75D);
    private static final Vec3[] CARGO_SLOTS = {new Vec3(0.0D, 1.375D, 2.25D), new Vec3(0.0D, 1.375D, -1.875D)};
    /** Height of the cushion: the hull hovers this far above water or ground. */
    private static final double HOVER = 0.35D;

    public TitanLcacHovercraftEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.2F); // the skirt climbs onto the beach
    }

    public static AttributeSupplier.Builder createLcacAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 600.0D)
                .add(Attributes.ARMOR, 18.0D);
    }

    @Override
    public int getCargoCapacity() {
        return 2;
    }

    @Override
    protected boolean shouldTitanKneel() {
        return false;
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return DRIVER_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return CARGO_SLOTS[Math.min(slotIndex, CARGO_SLOTS.length - 1)];
    }

    /** The open deck (top 1.375 blocks, 4 wide) is solid and carries whatever stands or parks on it while the craft skims along. */
    @Override
    protected void spawnDeckColliders() {
        DeckColliderEntity.spawnRow(this, 4.0F, 1.0F, 0.0F, 0.375F, -4.9D, 5.1D);
    }

    /** Vertical speed that eases the hull to HOVER blocks above the water surface (null = no water under it). */
    private Double cushionLift() {
        // Steer to the surface itself, not "in water or not": that flips every tick and bounces the hull
        net.minecraft.core.BlockPos.MutableBlockPos p = net.minecraft.core.BlockPos.containing(this.getX(), this.getY() + 2.0D, this.getZ()).mutable();
        for (int i = 0; i < 5; i++, p.move(net.minecraft.core.Direction.DOWN)) {
            var fluid = this.level().getFluidState(p);
            if (fluid.is(FluidTags.WATER)) {
                double surface = p.getY() + fluid.getHeight(this.level(), p);
                return Mth.clamp((surface + HOVER - this.getY()) * 0.3D, -0.3D, 0.4D);
            }
        }
        return null;
    }

    @Override
    public void tick() {
        super.tick();
        // Air cushion: ride on top of the water, so the skirt clears the lip of the beach instead of hitting its side
        Double lift = cushionLift();
        if (lift != null && this.getControllingPassenger() == null) {
            Vec3 m = this.getDeltaMovement();
            this.setDeltaMovement(m.x * 0.9D, lift, m.z * 0.9D);
            this.move(MoverType.SELF, this.getDeltaMovement());
        }
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        // Drives predictably like a boat on land and water
        updateThrottle(driver, 0.9F, 0.3F, 0.03F, 0.05F, 0.01F);
        this.yawDelta = -driver.xxa * 2.2F;
        Double lift = cushionLift();
        double vert = lift != null ? lift : gravityMotion();
        moveAlongHeading(0.82F, vert); // Stable hover grip: no wild drill-spinning

        if (this.level().isClientSide && this.tickCount % 2 == 0) {
            // Spray / dust thrown out from under the skirt
            boolean water = this.isInWater() || this.level().getFluidState(this.blockPosition().below()).is(FluidTags.WATER);
            for (int i = 0; i < 3; i++) {
                double a = this.random.nextDouble() * Math.PI * 2.0D;
                this.level().addParticle(water ? ParticleTypes.SPLASH : ParticleTypes.POOF,
                        this.getX() + Math.cos(a) * 3.6D, this.getY() + 0.1D, this.getZ() + Math.sin(a) * 5.5D,
                        Math.cos(a) * 0.15D, 0.05D, Math.sin(a) * 0.15D);
            }
        }
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "controller", 4, state -> {
            if (this.getControllingPassenger() != null) {
                return state.setAndContinue(RawAnimation.begin().thenLoop("animation.lcac_hovercraft.hover"));
            }
            return state.setAndContinue(RawAnimation.begin().thenLoop("animation.lcac_hovercraft.idle"));
        }));
    }
}
