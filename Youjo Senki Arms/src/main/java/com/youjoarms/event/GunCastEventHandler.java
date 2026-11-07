package com.youjoarms.event;

import com.tacz.guns.api.event.common.EntityHurtByGunEvent;
import com.tacz.guns.api.event.common.GunShootEvent;
import com.tacz.guns.api.event.server.AmmoHitBlockEvent;
import com.tacz.guns.api.item.IGun;
import com.youjoarms.capability.PlayerMageData;
import com.youjoarms.capability.PlayerMageProvider;
import com.youjoarms.config.YoujoArmsConfig;
import com.youjoarms.entity.ArtilleryShellEntity;
import com.youjoarms.entity.FormulaZoneEntity;
import com.youjoarms.formula.FormulaType;
import com.youjoarms.network.PacketSyncMageDataS2C;
import com.youjoarms.network.YoujoArmsNetwork;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.AttachCapabilitiesEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Mod.EventBusSubscriber(modid = "youjoarms", bus = Mod.EventBusSubscriber.Bus.FORGE)
public class GunCastEventHandler {

    /** The formula riding on a shooter's last bullet; it ends at the first impact or when the bullet would be gone. */
    private record ShotFormula(FormulaType formula, long expiresAt) {}

    private static final Map<UUID, ShotFormula> ACTIVE_SHOT_FORMULAS = new ConcurrentHashMap<>();
    private static final int SHOT_LIFETIME_TICKS = 60;

    /** Takes (and clears) the formula on the shooter's bullet, if it is still live. */
    private static FormulaType takeShotFormula(Entity shooter) {
        ShotFormula shot = ACTIVE_SHOT_FORMULAS.remove(shooter.getUUID());
        if (shot == null || shot.expiresAt() < shooter.level().getGameTime()) return null;
        return shot.formula();
    }

    @SubscribeEvent
    public static void onAttachCapabilities(AttachCapabilitiesEvent<net.minecraft.world.entity.Entity> event) {
        if (event.getObject() instanceof Player) {
            if (!event.getObject().getCapability(PlayerMageProvider.MAGE_DATA).isPresent()) {
                event.addCapability(new ResourceLocation("youjoarms", "mage_data"), new PlayerMageProvider());
            }
        }
    }

    @SubscribeEvent
    public static void onPlayerClone(PlayerEvent.Clone event) {
        event.getOriginal().getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(oldCap -> {
            event.getEntity().getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(newCap -> {
                newCap.copyFrom(oldCap);
            });
        });
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Player player = event.player;

        player.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(cap -> {
            cap.applyProfile(com.youjoarms.mana.GunMana.of(player.getMainHandItem()));
            // Recharge the held gun's Mana Cell: sneak with Amethyst Shards in the off hand, one shard a second
            if (!player.level().isClientSide && player.isShiftKeyDown() && player.tickCount % 20 == 0) {
                ItemStack held = player.getMainHandItem();
                int tier = com.youjoarms.mana.GunMana.cellTier(held);
                ItemStack off = player.getOffhandItem();
                if (tier > 0 && off.is(net.minecraft.world.item.Items.AMETHYST_SHARD)
                        && com.youjoarms.mana.GunMana.charge(held) < com.youjoarms.mana.GunMana.CHARGE_CAPACITY) {
                    off.shrink(1);
                    com.youjoarms.mana.GunMana.setCharge(held, com.youjoarms.mana.GunMana.charge(held) + com.youjoarms.mana.GunMana.chargePerShard(tier));
                    ((ServerLevel) player.level()).sendParticles(ParticleTypes.GLOW, player.getX(), player.getEyeY() - 0.3, player.getZ(), 6, 0.3, 0.3, 0.3, 0.02);
                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 0.8f, 1.2f);
                }
            }
            // Tick charging
            if (cap.isCharging()) {
                cap.tickCharge();
            }
            if (cap.getShieldTicks() > 0) {
                cap.setShieldTicks(cap.getShieldTicks() - 1);
                if (cap.getShieldTicks() == 0 && player instanceof ServerPlayer sp) syncToPlayer(sp, cap);
            }

            // Mana regen (once per second on server)
            if (!player.level().isClientSide && player.tickCount % 20 == 0) {
                int regen = cap.getRegenPerSecond();
                if (regen > 0 && cap.getMana() < cap.getMaxMana()) {
                    cap.regen(regen);
                    syncToPlayer((ServerPlayer) player, cap);
                }
            }
        });
    }

    @SubscribeEvent
    public static void onGunShoot(GunShootEvent event) {
        LivingEntity shooter = event.getShooter();
        if (!(shooter instanceof ServerPlayer player)) return;

        ItemStack gunStack = event.getGunItemStack();
        IGun gun = IGun.getIGunOrNull(gunStack);
        if (gun == null) return;

        player.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(cap -> {
            FormulaType formula = cap.getSelectedFormula();
            if (formula == FormulaType.NONE) return;

            // Check if fully charged
            if (!cap.isFullyCharged()) {
                return;
            }

            int cost = Math.max(1, (int) Math.round(formula.getManaCost() * cap.getCostMultiplier()));
            if (!cap.consumeMana(cost)) {
                // Not enough mana
                player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0f, 1.2f);
                return;
            }

            if (com.youjoarms.mana.GunMana.cellTier(gunStack) > 0) {
                com.youjoarms.mana.GunMana.setCharge(gunStack, com.youjoarms.mana.GunMana.charge(gunStack) - 1);
            }
            // Cast successful!
            player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.EVOKER_CAST_SPELL, SoundSource.PLAYERS, 1.0f, 1.5f);

            // Spawn muzzle spell burst particles
            if (player.level() instanceof ServerLevel serverLevel) {
                Vec3 look = player.getLookAngle();
                double px = player.getX() + look.x * 2.5;
                double py = player.getEyeY() + look.y * 2.5;
                double pz = player.getZ() + look.z * 2.5;
                serverLevel.sendParticles(ParticleTypes.END_ROD, px, py, pz, 12, 0.4, 0.4, 0.4, 0.08);
            }

            switch (formula) {
                case ARTILLERY -> {
                    event.setCanceled(true);  // the shell replaces the TACZ bullet
                    ArtilleryShellEntity shell = new ArtilleryShellEntity(player.level(), player);
                    shell.shootFromRotation(player, player.getXRot(), player.getYRot(), 0.0F, 2.5F, 1.0F);
                    player.level().addFreshEntity(shell);
                    gun.reduceCurrentAmmoCount(gunStack);
                }
                case BARRAGE -> {
                    event.setCanceled(true);
                    int bolts = YoujoArmsConfig.COMMON.barrageBolts.get();
                    for (int i = 0; i < bolts; i++) {  // fan spread across 40 degrees
                        float yawOffset = bolts == 1 ? 0 : -20F + 40F * i / (bolts - 1);
                        ArtilleryShellEntity bolt = ArtilleryShellEntity.bolt(player.level(), player);
                        bolt.shootFromRotation(player, player.getXRot(), player.getYRot() + yawOffset, 0.0F, 3.2F, 0.5F);
                        player.level().addFreshEntity(bolt);
                    }
                    gun.reduceCurrentAmmoCount(gunStack);
                }
                case SHIELD -> {
                    event.setCanceled(true);  // the shell is cast, not fired: no ammo spent
                    cap.setShieldTicks(YoujoArmsConfig.COMMON.shieldDurationTicks.get());
                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.BEACON_POWER_SELECT, SoundSource.PLAYERS, 1.2f, 1.4f);
                }
                case ULTIMATE -> {
                    event.setCanceled(true);
                    HitResult hit = player.pick(160.0D, 1.0F, false);
                    Vec3 at = hit.getLocation();
                    player.level().addFreshEntity(new FormulaZoneEntity(player.level(), formula, at.x, at.y, at.z, player));
                    gun.reduceCurrentAmmoCount(gunStack);
                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.WITHER_SPAWN, SoundSource.PLAYERS, 1.0f, 1.6f);
                }
                default -> ACTIVE_SHOT_FORMULAS.put(player.getUUID(),
                        new ShotFormula(formula, player.level().getGameTime() + SHOT_LIFETIME_TICKS));
            }

            // Reset charge state after firing
            cap.setCharging(false);
            syncToPlayer(player, cap);
        });
    }

    @SubscribeEvent
    public static void onEntityHurtByGunPre(EntityHurtByGunEvent.Pre event) {
        LivingEntity attacker = event.getAttacker();
        if (attacker == null || attacker.level().isClientSide) return;

        FormulaType formula = takeShotFormula(attacker);
        if (formula == null) return;

        Vec3 pos = event.getHurtEntity().position();
        switch (formula) {
            case PIERCING -> {
                double multiplier = YoujoArmsConfig.COMMON.piercingDamageMultiplier.get();
                event.setBaseAmount((float) (event.getBaseAmount() * multiplier));
                event.setHeadshotMultiplier(event.getHeadshotMultiplier() * 1.25f);
            }
            case EXPLOSIVE -> explode(attacker.level(), pos);
            case AREA -> attacker.level().addFreshEntity(new FormulaZoneEntity(attacker.level(), formula, pos.x, pos.y, pos.z, attacker));
            default -> {}
        }
    }

    @SubscribeEvent
    public static void onAmmoHitBlock(AmmoHitBlockEvent event) {
        Level level = event.getLevel();
        if (level.isClientSide || !(event.getAmmo().getOwner() instanceof LivingEntity shooter)) return;
        FormulaType formula = takeShotFormula(shooter);
        if (formula == null) return;

        Vec3 hit = event.getHitResult().getLocation();
        if (formula == FormulaType.EXPLOSIVE) {
            explode(level, hit);
        } else if (formula == FormulaType.AREA) {
            level.addFreshEntity(new FormulaZoneEntity(level, formula, hit.x, hit.y, hit.z, shooter));
        }
    }

    /** Defensive Shell: soak most damage while it is up. */
    @SubscribeEvent
    public static void onLivingHurt(LivingHurtEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        player.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(cap -> {
            if (cap.getShieldTicks() <= 0) return;
            event.setAmount((float) (event.getAmount() * (1.0 - YoujoArmsConfig.COMMON.shieldDamageReduction.get())));
            player.serverLevel().sendParticles(ParticleTypes.ENCHANTED_HIT, player.getX(), player.getY() + 1, player.getZ(),
                    20, 0.7, 0.9, 0.7, 0.2);
            player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.AMETHYST_BLOCK_HIT, SoundSource.PLAYERS, 1.5f, 0.8f);
        });
    }

    private static void explode(Level level, Vec3 pos) {
        double radius = YoujoArmsConfig.COMMON.explosiveRadius.get();
        boolean blockDamage = YoujoArmsConfig.COMMON.explosiveBlockDamage.get();
        level.explode(null, pos.x, pos.y, pos.z, (float) radius,
                blockDamage ? Level.ExplosionInteraction.MOB : Level.ExplosionInteraction.NONE);
    }

    private static void syncToPlayer(ServerPlayer player, PlayerMageData cap) {
        PacketSyncMageDataS2C packet = new PacketSyncMageDataS2C(player, cap);
        YoujoArmsNetwork.CHANNEL.send(PacketDistributor.TRACKING_ENTITY_AND_SELF.with(() -> player), packet);
    }
}
