package com.youjoarms.entity;

import com.youjoarms.config.YoujoArmsConfig;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.network.NetworkHooks;
import org.joml.Vector3f;

/** Artillery formula shell (arcing, big blast) or, with {@code bolt}, one of the Barrage formula's magic bolts. */
public class ArtilleryShellEntity extends ThrowableItemProjectile {
    private static final EntityDataAccessor<Boolean> BOLT = SynchedEntityData.defineId(ArtilleryShellEntity.class, EntityDataSerializers.BOOLEAN);
    private static final DustParticleOptions BOLT_DUST = new DustParticleOptions(new Vector3f(0.75F, 0.45F, 1.0F), 1.4F);

    public ArtilleryShellEntity(EntityType<? extends ThrowableItemProjectile> type, Level level) {
        super(type, level);
    }

    public ArtilleryShellEntity(Level level, LivingEntity shooter) {
        super(ModEntities.ARTILLERY_SHELL.get(), shooter, level);
    }

    public static ArtilleryShellEntity bolt(Level level, LivingEntity shooter) {
        ArtilleryShellEntity e = new ArtilleryShellEntity(level, shooter);
        e.entityData.set(BOLT, true);
        return e;
    }

    public boolean isBolt() {
        return entityData.get(BOLT);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(BOLT, false);
    }

    @Override
    protected float getGravity() {
        return isBolt() ? 0.002F : super.getGravity();
    }

    @Override
    protected Item getDefaultItem() {
        return Items.FIREWORK_STAR;
    }

    @Override
    public void tick() {
        super.tick();
        if (!this.level().isClientSide) {
            if (isBolt() && tickCount > 60) discard();
            return;
        }
        for (int i = 0; i < 3; i++) {
            double px = getX() + (random.nextDouble() - 0.5) * 0.2;
            double py = getY() + (random.nextDouble() - 0.5) * 0.2;
            double pz = getZ() + (random.nextDouble() - 0.5) * 0.2;
            if (isBolt()) {
                level().addParticle(BOLT_DUST, px, py, pz, 0, 0, 0);
            } else {
                level().addParticle(ParticleTypes.SOUL_FIRE_FLAME, px, py, pz, 0, 0, 0);
            }
            level().addParticle(ParticleTypes.END_ROD, px, py, pz, 0, 0, 0);
        }
    }

    @Override
    protected void onHit(HitResult hitResult) {
        super.onHit(hitResult);
        if (this.level().isClientSide) return;
        ServerLevel serverLevel = (ServerLevel) this.level();
        if (isBolt()) {
            if (hitResult instanceof EntityHitResult ehr && ehr.getEntity() != getOwner()) {
                ehr.getEntity().hurt(damageSources().indirectMagic(this, getOwner()),
                        YoujoArmsConfig.COMMON.barrageBoltDamage.get().floatValue());
            }
            serverLevel.sendParticles(BOLT_DUST, getX(), getY(), getZ(), 12, 0.25, 0.25, 0.25, 0.05);
            serverLevel.sendParticles(ParticleTypes.END_ROD, getX(), getY(), getZ(), 6, 0.1, 0.1, 0.1, 0.12);
        } else {
            double radius = YoujoArmsConfig.COMMON.artilleryExplosionRadius.get();
            boolean blockDamage = YoujoArmsConfig.COMMON.artilleryBlockDamage.get();
            level().explode(this, getX(), getY(), getZ(), (float) radius,
                    blockDamage ? Level.ExplosionInteraction.MOB : Level.ExplosionInteraction.NONE);
            serverLevel.sendParticles(ParticleTypes.FLASH, getX(), getY(), getZ(), 5, 0.5, 0.5, 0.5, 0.1);
            serverLevel.sendParticles(ParticleTypes.EXPLOSION_EMITTER, getX(), getY(), getZ(), 1, 0, 0, 0, 0);
        }
        this.discard();
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Bolt", isBolt());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        entityData.set(BOLT, tag.getBoolean("Bolt"));
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
