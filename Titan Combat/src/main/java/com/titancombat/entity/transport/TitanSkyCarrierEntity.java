package com.titancombat.entity.transport;

import com.titancombat.util.InputHelper;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;

/**
 * Flying carrier: a 48-block flight deck on four lift pods. Players walk on the deck and aircraft land and park on it
 * (DeckColliderEntity tiles carry them), and it hangs where it was left when abandoned instead of sinking.
 * Model: scripts/gen_naval_fleet.py. Deck top 3.25 blocks, island at x +3.75..+6.9, z -1.9..+5.6.
 */
public class TitanSkyCarrierEntity extends BaseTransportVehicleEntity {
    public TitanSkyCarrierEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(0.6F);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createTransportAttributes().add(Attributes.MAX_HEALTH, 1200.0D).add(Attributes.ARMOR, 34.0D).add(Attributes.ARMOR_TOUGHNESS, 16.0D);
    }

    @Override public boolean isAircraft() { return true; }
    @Override public int getCargoCapacity() { return 2; }
    @Override protected Vec3 getDriverSeatOffset() { return new Vec3(5.3D, 6.625D - 0.6D, 2.2D); }
    @Override protected Vec3 getTitanCargoOffset(int slotIndex) { return new Vec3(-1.5D, 3.3D, slotIndex == 0 ? -6.0D : -15.0D); }

    @Override
    public Vec3 getDismountLocationForPassenger(LivingEntity passenger) {
        double yawRad = Math.toRadians(this.getYRot()); // onto the deck, never into the sky
        double lx = 0.0D, lz = -3.0D;
        return new Vec3(this.getX() + lx * Math.cos(yawRad) - lz * Math.sin(yawRad), this.getY() + 3.3D, this.getZ() + lx * Math.sin(yawRad) + lz * Math.cos(yawRad));
    }

    @Override
    protected void spawnDeckColliders() {
        DeckColliderEntity.spawnRow(this, 14.0F, 3.0F, 0.0F, 0.25F, -24.0D, 24.0D);          // flight deck (top 3.25)
        DeckColliderEntity.spawnRow(this, 3.1F, 4.9F, 5.3F, 3.25F, -1.9D, 5.6D);             // island
    }

    @Override
    public void tick() {
        super.tick();
        // Lift holds it in the air with nobody at the helm; only a wrecked or (while manned) starved engine drops it
        boolean lifting = !isPropulsionDestroyed() && (getEnergy() > 0 || this.getControllingPassenger() == null);
        this.setNoGravity(lifting);
        if (lifting && this.getControllingPassenger() == null && !this.level().isClientSide) {
            this.setDeltaMovement(Vec3.ZERO);
            this.currentSpeed = 0.0F;
        }
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        this.yawDelta = Math.abs(driver.xxa) > 0.01F ? -driver.xxa * 0.7F : 0.0F;
        this.setYRot(this.getYRot() + this.yawDelta);

        double vertical = InputHelper.isJumping(driver) ? 0.22D : TitanSkyCraneDroneEntity.clientDescendHeld ? -0.2D : 0.0D;
        this.currentSpeed = approach(this.currentSpeed, driver.zza * 0.5F, 0.012F);
        double yawRad = Math.toRadians(this.getYRot());
        this.setDeltaMovement(-Math.sin(yawRad) * this.currentSpeed, vertical, Math.cos(yawRad) * this.currentSpeed);
        this.move(MoverType.SELF, this.getDeltaMovement());
        this.resetFallDistance();
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "lift", 4, event -> event.setAndContinue(RawAnimation.begin().thenLoop(
                this.getControllingPassenger() != null || !this.onGround() ? "animation.sky_carrier.fly" : "animation.sky_carrier.idle"))));
    }
}
