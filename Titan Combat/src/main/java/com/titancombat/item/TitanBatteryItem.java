package com.titancombat.item;

import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import com.titancombat.sound.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class TitanBatteryItem extends Item {
    public static final int TIER_1_CAPACITY = 10000;
    public static final int TIER_2_CAPACITY = 50000;
    public static final int TIER_3_CAPACITY = 250000;
    public static final int MAX_ENERGY = TIER_1_CAPACITY;

    private final int capacity;

    public TitanBatteryItem(int capacity, Properties properties) {
        super(properties);
        this.capacity = capacity;
    }

    public TitanBatteryItem(Properties properties) {
        this(TIER_1_CAPACITY, properties);
    }

    public int getCapacity() {
        return this.capacity;
    }

    public static int getCapacity(ItemStack stack) {
        if (!stack.isEmpty() && stack.getItem() instanceof TitanBatteryItem bat) {
            return bat.getCapacity();
        }
        return TIER_1_CAPACITY;
    }

    public static int getEnergy(ItemStack stack) {
        if (stack.isEmpty()) return 0;
        CompoundTag tag = stack.getTag();
        if (tag != null && tag.contains("Energy")) {
            return tag.getInt("Energy");
        }
        // Default freshly created batteries to full charge, unless empty_battery
        if (stack.is(ModItems.EMPTY_BATTERY.get())) {
            return 0;
        }
        return getCapacity(stack);
    }

    public static void setEnergy(ItemStack stack, int energy) {
        int cap = getCapacity(stack);
        energy = Mth.clamp(energy, 0, cap);
        stack.getOrCreateTag().putInt("Energy", energy);
    }

    @Override
    public boolean isBarVisible(ItemStack stack) {
        return true;
    }

    @Override
    public int getBarWidth(ItemStack stack) {
        int cap = getCapacity(stack);
        return Math.round(13.0F * (float) getEnergy(stack) / (float) Math.max(1, cap));
    }

    @Override
    public int getBarColor(ItemStack stack) {
        int cap = getCapacity(stack);
        float pct = (float) getEnergy(stack) / (float) Math.max(1, cap);
        if (pct < 0.20F) return 0xFF2A44; // Red (< 20%)
        if (pct < 0.50F) return 0xFFB300; // Amber (< 50%)
        return 0x00E5FF; // Electric Cyan
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        int energy = getEnergy(stack);
        int cap = getCapacity(stack);
        int pct = Math.round((float) energy * 100.0F / (float) Math.max(1, cap));
        String pctColor = energy == 0 ? "§c" : (energy >= cap ? "§a" : "§e");
        tooltip.add(Component.translatable("tooltip.titancombat.battery_energy",
                String.format("%,d", energy), String.format("%,d", cap), pctColor + pct + "%"));
        if (energy <= 0) {
            tooltip.add(Component.translatable("tooltip.titancombat.battery_depleted"));
        } else if (energy >= cap) {
            tooltip.add(Component.translatable("tooltip.titancombat.battery_ready"));
        } else {
            tooltip.add(Component.translatable("tooltip.titancombat.battery_charging", pct));
        }
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        // 1. Refuel Titan Mechs (50,000 FE reactor)
        if (target instanceof BaseMechEntity mech) {
            int batteryEnergy = getEnergy(stack);
            if (batteryEnergy <= 0) {
                if (!player.level().isClientSide) {
                    player.sendSystemMessage(Component.translatable("message.titancombat.battery_empty_insert"));
                }
                return InteractionResult.sidedSuccess(player.level().isClientSide);
            }

            int curMechEnergy = mech.getEnergy();
            int maxMechEnergy = mech.getMaxEnergy();

            if (curMechEnergy >= maxMechEnergy && mech.getShield() >= mech.getMaxShield()) {
                if (!player.level().isClientSide) {
                    player.sendSystemMessage(Component.translatable("message.titancombat.reactor_already_full"));
                }
                return InteractionResult.sidedSuccess(player.level().isClientSide);
            }

            int neededEnergy = maxMechEnergy - curMechEnergy;
            int transferEnergy = Math.min(neededEnergy, batteryEnergy);
            mech.addEnergy(transferEnergy);
            int remainingBattery = batteryEnergy - transferEnergy;

            // Overflow charges shield
            if (remainingBattery > 0 && mech.getShield() < mech.getMaxShield()) {
                float neededShield = mech.getMaxShield() - mech.getShield();
                float shieldTransfer = Math.min(neededShield, (float) remainingBattery / 4.0F);
                mech.setShield(mech.getShield() + shieldTransfer);
                remainingBattery -= (int) (shieldTransfer * 4.0F);
            }

            setEnergy(stack, remainingBattery);

            // Sounds & Particles
            player.level().playSound(null, mech.blockPosition(), ModSounds.TITAN_GET_BATTERY.get(), SoundSource.PLAYERS, 1.5F, 1.0F);
            player.level().playSound(null, mech.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 1.2F, 1.8F);

            if (player.level().isClientSide) {
                for (int i = 0; i < 16; i++) {
                    double px = mech.getX() + (player.getRandom().nextDouble() - 0.5D) * 2.5D;
                    double py = mech.getY() + 1.5D + player.getRandom().nextDouble() * 2.0D;
                    double pz = mech.getZ() + (player.getRandom().nextDouble() - 0.5D) * 2.5D;
                    player.level().addParticle(ParticleTypes.ELECTRIC_SPARK, px, py, pz, 0, 0.1D, 0);
                }
            } else {
                player.sendSystemMessage(Component.translatable("message.titancombat.battery_inserted",
                        String.format("%,d", transferEnergy),
                        String.format("%,d", mech.getEnergy()),
                        String.format("%,d", maxMechEnergy)));
            }

            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }

        // 2. Refuel Transport Vehicles (100,000 FE fuel cell)
        if (target instanceof BaseTransportVehicleEntity vehicle) {
            int batteryEnergy = getEnergy(stack);
            if (batteryEnergy <= 0) {
                if (!player.level().isClientSide) {
                    player.sendSystemMessage(Component.literal("§c[LOGISTICS] Battery is completely depleted! Charge it in a Battery Charger."));
                }
                return InteractionResult.sidedSuccess(player.level().isClientSide);
            }
            if (vehicle.getEnergy() >= vehicle.getMaxEnergy()) {
                if (!player.level().isClientSide) {
                    player.sendSystemMessage(Component.literal("§e[LOGISTICS] Vehicle fuel cell is already at 100% capacity (" + String.format("%,d", vehicle.getMaxEnergy()) + " FE)!"));
                }
                return InteractionResult.sidedSuccess(player.level().isClientSide);
            }
            int needed = vehicle.getMaxEnergy() - vehicle.getEnergy();
            int transfer = Math.min(needed, batteryEnergy);
            vehicle.addEnergy(transfer);
            setEnergy(stack, batteryEnergy - transfer);

            player.level().playSound(null, vehicle.blockPosition(), SoundEvents.EXPERIENCE_ORB_PICKUP, SoundSource.PLAYERS, 1.2F, 1.4F);
            player.level().playSound(null, vehicle.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 0.8F, 1.8F);
            if (!player.level().isClientSide) {
                player.sendSystemMessage(Component.literal(String.format("§a[LOGISTICS] Vehicle Engine Refueled: +%,d FE (%,d / %,d FE | %d%%)",
                        transfer, vehicle.getEnergy(), vehicle.getMaxEnergy(), Math.round((float) vehicle.getEnergy() * 100.0F / (float) vehicle.getMaxEnergy()))));
            }
            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }

        return super.interactLivingEntity(stack, player, target, hand);
    }
}
