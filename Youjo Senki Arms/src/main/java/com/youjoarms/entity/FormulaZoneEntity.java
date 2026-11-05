package com.youjoarms.entity;

import com.youjoarms.config.YoujoArmsConfig;
import com.youjoarms.formula.FormulaType;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.entity.IEntityAdditionalSpawnData;
import net.minecraftforge.network.NetworkHooks;

import javax.annotation.Nullable;
import java.util.UUID;

/**
 * A formula that lands somewhere and goes off after a fuse: Area Suppression (ground circle) or
 * Annihilation (ground circle + stacked sky circles). It has no model; MagicCircleRenderer draws it.
 */
public class FormulaZoneEntity extends Entity implements IEntityAdditionalSpawnData {
    private static final EntityDataAccessor<Integer> FORMULA = SynchedEntityData.defineId(FormulaZoneEntity.class, EntityDataSerializers.INT);
    @Nullable
    private UUID ownerId;

    public FormulaZoneEntity(EntityType<?> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public FormulaZoneEntity(Level level, FormulaType formula, double x, double y, double z, @Nullable LivingEntity owner) {
        this(ModEntities.FORMULA_ZONE.get(), level);
        entityData.set(FORMULA, formula.getId());
        setPos(x, y, z);
        ownerId = owner != null ? owner.getUUID() : null;
    }

    public FormulaType getFormula() {
        return FormulaType.byId(entityData.get(FORMULA));
    }

    /** Ticks from landing to detonation. */
    public int getFuse() {
        return getFormula() == FormulaType.ULTIMATE ? 60 : 30;
    }

    public float getRadius() {
        var radius = getFormula() == FormulaType.ULTIMATE ? YoujoArmsConfig.COMMON.ultimateRadius : YoujoArmsConfig.COMMON.areaRadius;
        return radius.get().floatValue();
    }

    @Override
    protected void defineSynchedData() {
        entityData.define(FORMULA, FormulaType.AREA.getId());
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) return;
        ServerLevel level = (ServerLevel) level();
        int fuse = getFuse();
        if (tickCount == 1) {
            level.playSound(null, getX(), getY(), getZ(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 3.0F, 1.6F);
        }
        if (tickCount < fuse && tickCount % 5 == 0) {
            float r = getRadius() * tickCount / fuse;
            level.sendParticles(ParticleTypes.END_ROD, getX(), getY() + 0.2, getZ(), 10, r * 0.5, 0.1, r * 0.5, 0.02);
        }
        if (tickCount == fuse) detonate(level);
        if (tickCount > fuse + 20) discard();  // linger so the release flash finishes rendering
    }

    private void detonate(ServerLevel level) {
        float radius = getRadius();
        Entity owner = ownerId != null ? level.getEntity(ownerId) : null;
        if (getFormula() == FormulaType.ULTIMATE) {
            boolean blocks = YoujoArmsConfig.COMMON.ultimateBlockDamage.get();
            Level.ExplosionInteraction mode = blocks ? Level.ExplosionInteraction.MOB : Level.ExplosionInteraction.NONE;
            level.explode(owner, getX(), getY(), getZ(), radius * 0.6F, mode);
            for (int i = 0; i < 6; i++) {  // ring of secondary blasts
                double a = i * Math.PI / 3;
                level.explode(owner, getX() + Math.cos(a) * radius * 0.6, getY(), getZ() + Math.sin(a) * radius * 0.6, radius * 0.35F, mode);
            }
            for (int i = 0; i < 3; i++) {
                LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
                if (bolt != null) {
                    bolt.moveTo(getX() + (random.nextDouble() - 0.5) * radius, getY(), getZ() + (random.nextDouble() - 0.5) * radius);
                    bolt.setVisualOnly(true);
                    level.addFreshEntity(bolt);
                }
            }
            level.sendParticles(ParticleTypes.EXPLOSION_EMITTER, getX(), getY() + 1, getZ(), 4, radius * 0.3, 0.5, radius * 0.3, 0);
        } else {
            float damage = YoujoArmsConfig.COMMON.areaDamage.get().floatValue();
            for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(getX() - radius, getY() - 2, getZ() - radius,
                    getX() + radius, getY() + 4, getZ() + radius), e -> e.distanceToSqr(this) <= radius * radius && e != owner)) {
                e.hurt(damageSources().indirectMagic(this, owner), damage);
            }
            level.sendParticles(ParticleTypes.EXPLOSION, getX(), getY() + 0.5, getZ(), 24, radius * 0.4, 0.4, radius * 0.4, 0);
            level.sendParticles(ParticleTypes.FLASH, getX(), getY() + 0.5, getZ(), 2, 0, 0, 0, 0);
            level.playSound(null, getX(), getY(), getZ(), SoundEvents.GENERIC_EXPLODE, SoundSource.PLAYERS, 4.0F, 0.8F);
        }
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        entityData.set(FORMULA, tag.getInt("Formula"));
        if (tag.hasUUID("Owner")) ownerId = tag.getUUID("Owner");
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
        tag.putInt("Formula", entityData.get(FORMULA));
        if (ownerId != null) tag.putUUID("Owner", ownerId);
    }

    // the formula travels in the spawn packet so the client draws the right zone from its first frame
    @Override
    public void writeSpawnData(FriendlyByteBuf buf) {
        buf.writeVarInt(entityData.get(FORMULA));
    }

    @Override
    public void readSpawnData(FriendlyByteBuf buf) {
        entityData.set(FORMULA, buf.readVarInt());
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distance) {
        return distance < 256 * 256;
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
