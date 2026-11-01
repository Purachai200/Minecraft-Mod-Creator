package com.obsolete.entity;

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

public class ExoframeCasingEntity extends Entity {
    public float prevPitch, prevYaw, prevRoll;
    public float pitch, yaw, roll;
    public float pitchSpin, yawSpin, rollSpin;

    private boolean clientSpinInitialized = false;
    private int age = 0;

    public ExoframeCasingEntity(EntityType<?> type, Level level) {
        super(type, level);
        this.noPhysics = false;
    }

    public ExoframeCasingEntity(Level level, Vec3 pos, Vec3 forward, Vec3 right) {
        this(ModEntities.CASING.get(), level);
        this.setPos(pos.x, pos.y, pos.z);

        // Fling casing violently rightward and slightly up/backwards from ejection port
        double rightForce = 0.22D + (this.random.nextDouble() * 0.09D);
        double upForce = 0.16D + (this.random.nextDouble() * 0.08D);
        double backForce = -0.04D + (this.random.nextDouble() * 0.08D);

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

        this.pitchSpin = 20.0F + this.random.nextFloat() * 25.0F;
        this.rollSpin = 15.0F + this.random.nextFloat() * 20.0F;
        this.yawSpin = 12.0F + this.random.nextFloat() * 15.0F;
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
        if (this.age > 120) { // Despawn after 6 seconds
            this.discard();
            return;
        }

        // Client-side spin initialization and hot brass smoke wisps
        if (this.level().isClientSide) {
            if (!this.clientSpinInitialized) {
                this.clientSpinInitialized = true;
                this.pitch = (this.getId() * 37.0F) % 360.0F;
                this.yaw = (this.getId() * 67.0F) % 360.0F;
                this.roll = (this.getId() * 97.0F) % 360.0F;
                this.prevPitch = this.pitch;
                this.prevYaw = this.yaw;
                this.prevRoll = this.roll;

                this.pitchSpin = 18.0F + (this.getId() % 11) * 2.5F;
                this.rollSpin = 14.0F + (this.getId() % 7) * 2.0F;
                this.yawSpin = 10.0F + (this.getId() % 5) * 1.8F;
            }

            // Fresh scorching hot brass smoke wisp for the first second
            if (this.age < 22 && this.random.nextFloat() < 0.35F) {
                this.level().addParticle(ParticleTypes.SMOKE,
                        this.getX() + (this.random.nextDouble() - 0.5D) * 0.05D,
                        this.getY() + 0.05D,
                        this.getZ() + (this.random.nextDouble() - 0.5D) * 0.05D,
                        0.0D, 0.012D, 0.0D);
            }
        }

        // Tumbling rotation
        this.prevPitch = this.pitch;
        this.pitch += this.pitchSpin;
        this.prevYaw = this.yaw;
        this.yaw += this.yawSpin;
        this.prevRoll = this.roll;
        this.roll += this.rollSpin;

        // Apply physics gravity and drag
        Vec3 motion = this.getDeltaMovement();
        if (!this.onGround()) {
            motion = motion.add(0.0D, -0.04D, 0.0D); // Gravity
        }
        motion = motion.scale(0.98D); // Air friction
        this.setDeltaMovement(motion);

        Vec3 oldMotion = this.getDeltaMovement();
        this.move(MoverType.SELF, this.getDeltaMovement());

        // Handle ground and wall collisions
        if (this.onGround()) {
            if (Math.abs(oldMotion.y) > 0.07D) {
                // Bounce off ground
                this.setDeltaMovement(this.getDeltaMovement().x * 0.55D, -oldMotion.y * 0.42D, this.getDeltaMovement().z * 0.55D);
                this.pitchSpin *= 0.5F;
                this.rollSpin *= 0.5F;
                this.yawSpin *= 0.5F;

                // Metallic brass bounce clink
                float bouncePitch = 1.35F + this.random.nextFloat() * 0.35F;
                this.level().playSound(null, this.blockPosition(), SoundEvents.COPPER_STEP, SoundSource.PLAYERS, 0.85F, bouncePitch);
            } else {
                // Resting or skidding on ground
                this.setDeltaMovement(this.getDeltaMovement().multiply(0.65D, 0.0D, 0.65D));
                this.pitchSpin *= 0.3F;
                this.rollSpin *= 0.3F;
                this.yawSpin *= 0.3F;

                if (this.getDeltaMovement().horizontalDistanceSqr() < 0.001D) {
                    this.setDeltaMovement(Vec3.ZERO);
                    this.pitchSpin = 0.0F;
                    this.rollSpin = 0.0F;
                    this.yawSpin = 0.0F;
                    this.pitch = 0.0F; // Rest flat
                    this.roll = 0.0F;
                }
            }
        }

        if (this.horizontalCollision) {
            this.setDeltaMovement(-oldMotion.x * 0.4D, this.getDeltaMovement().y, -oldMotion.z * 0.4D);
            float clinkPitch = 1.4F + this.random.nextFloat() * 0.3F;
            this.level().playSound(null, this.blockPosition(), SoundEvents.COPPER_HIT, SoundSource.PLAYERS, 0.7F, clinkPitch);
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
