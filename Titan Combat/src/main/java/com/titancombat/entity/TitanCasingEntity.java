package com.titancombat.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;

public class TitanCasingEntity extends Entity {
    public float prevPitch, prevYaw, prevRoll;
    public float pitch, yaw, roll;
    public float pitchSpin, yawSpin, rollSpin;

    private boolean clientSpinInitialized = false;
    private int age = 0;

    public TitanCasingEntity(EntityType<?> type, Level level) {
        super(type, level);
        this.noPhysics = false;
    }

    public TitanCasingEntity(Level level, Vec3 pos, Vec3 forward, Vec3 right) {
        this(ModEntities.TITAN_CASING.get(), level);
        this.setPos(pos.x, pos.y, pos.z);

        // Fling heavy titan casing violently rightward, slightly upward and backward
        double rightForce = 0.35D + (this.random.nextDouble() * 0.12D);
        double upForce = 0.24D + (this.random.nextDouble() * 0.10D);
        double backForce = -0.06D + (this.random.nextDouble() * 0.10D);

        Vec3 ejectVel = right.scale(rightForce)
                .add(0.0D, upForce, 0.0D)
                .add(forward.scale(backForce));
        this.setDeltaMovement(ejectVel);

        this.pitch = this.random.nextFloat() * 360.0F;
        this.yaw = this.random.nextFloat() * 360.0F;
        this.roll = this.random.nextFloat() * 360.0F;
        this.prevPitch = this.pitch;
        this.prevYaw = this.yaw;
        this.prevRoll = this.roll;

        this.pitchSpin = 22.0F + this.random.nextFloat() * 26.0F;
        this.rollSpin = 18.0F + this.random.nextFloat() * 22.0F;
        this.yawSpin = 14.0F + this.random.nextFloat() * 16.0F;
    }

    @Override
    protected void defineSynchedData() {
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag compound) {
        this.age = compound.getInt("Age");
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag compound) {
        compound.putInt("Age", this.age);
    }

    @Override
    public void tick() {
        super.tick();
        this.age++;
        if (this.age > 160) { // Despawn after 8 seconds
            this.discard();
            return;
        }

        // Hot brass smoke wisps on client
        if (this.level().isClientSide) {
            if (!this.clientSpinInitialized) {
                this.clientSpinInitialized = true;
                this.pitch = (this.getId() * 37.0F) % 360.0F;
                this.yaw = (this.getId() * 67.0F) % 360.0F;
                this.roll = (this.getId() * 97.0F) % 360.0F;
                this.prevPitch = this.pitch;
                this.prevYaw = this.yaw;
                this.prevRoll = this.roll;

                this.pitchSpin = 20.0F + (this.getId() % 11) * 2.8F;
                this.rollSpin = 16.0F + (this.getId() % 7) * 2.2F;
                this.yawSpin = 12.0F + (this.getId() % 5) * 1.9F;
            }

            if (this.age < 30 && this.random.nextFloat() < 0.4F) {
                this.level().addParticle(ParticleTypes.SMOKE,
                        this.getX() + (this.random.nextDouble() - 0.5D) * 0.1D,
                        this.getY() + 0.1D,
                        this.getZ() + (this.random.nextDouble() - 0.5D) * 0.1D,
                        0.0D, 0.02D, 0.0D);
            }
        }

        // Tumbling rotation
        this.prevPitch = this.pitch;
        this.pitch += this.pitchSpin;
        this.prevYaw = this.yaw;
        this.yaw += this.yawSpin;
        this.prevRoll = this.roll;
        this.roll += this.rollSpin;

        // Apply physics
        Vec3 motion = this.getDeltaMovement();
        if (!this.onGround()) {
            motion = motion.add(0.0D, -0.05D, 0.0D); // Heavy gravity
        }
        motion = motion.scale(0.98D);
        this.setDeltaMovement(motion);

        Vec3 oldMotion = this.getDeltaMovement();
        this.move(MoverType.SELF, this.getDeltaMovement());

        // Handle ground collisions
        if (this.onGround()) {
            if (Math.abs(oldMotion.y) > 0.08D) {
                // Bounce
                this.setDeltaMovement(this.getDeltaMovement().x * 0.55D, -oldMotion.y * 0.40D, this.getDeltaMovement().z * 0.55D);
                this.pitchSpin *= 0.5F;
                this.rollSpin *= 0.5F;
                this.yawSpin *= 0.5F;

                // Heavy brass bounce clink
                float bouncePitch = 1.1F + this.random.nextFloat() * 0.3F;
                this.level().playSound(null, this.blockPosition(), SoundEvents.COPPER_STEP, SoundSource.PLAYERS, 1.1F, bouncePitch);
            } else {
                // Resting
                this.setDeltaMovement(this.getDeltaMovement().multiply(0.65D, 0.0D, 0.65D));
                this.pitchSpin *= 0.3F;
                this.rollSpin *= 0.3F;
                this.yawSpin *= 0.3F;

                if (this.getDeltaMovement().horizontalDistanceSqr() < 0.001D) {
                    this.setDeltaMovement(Vec3.ZERO);
                    this.pitchSpin = 0.0F;
                    this.rollSpin = 0.0F;
                    this.yawSpin = 0.0F;
                    this.pitch = 0.0F;
                    this.roll = 0.0F;
                }
            }
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
