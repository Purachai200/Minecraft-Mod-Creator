package com.obsolete.item;

import com.obsolete.energy.EnergyCapabilityProvider;
import com.obsolete.energy.ItemEnergyStorage;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.capabilities.ICapabilityProvider;
import net.minecraftforge.energy.IEnergyStorage;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExoframeFlightBoosterItem extends Item {

    public enum BoosterType {
        ROCKET_JETPACK("Jump-Jet Twin Rocket Pack", 250000, 2000, 25, 60, 1.0F, 1.45F, "High-thrust rocket thrusters for supersonic Gundam dash maneuvers."),
        VTOL_WINGS("VTOL Aero-Glide Wings", 180000, 1500, 12, 35, 1.35F, 1.15F, "Aerodynamic carbon wings for ultra-efficient high-speed cruising and diving."),
        DRONE_LIFTER("Heavy Lifter Quad-Rotor Drone", 300000, 2500, 18, 45, 0.90F, 1.65F, "High-torque quad rotors for massive vertical lift and rock-steady hover.");

        private final String displayName;
        private final int maxEnergy;
        private final int maxReceive;
        private final int hoverDrain;
        private final int boostDrain;
        private final float speedMultiplier;
        private final float climbMultiplier;
        private final String lore;

        BoosterType(String displayName, int maxEnergy, int maxReceive, int hoverDrain, int boostDrain, float speedMultiplier, float climbMultiplier, String lore) {
            this.displayName = displayName;
            this.maxEnergy = maxEnergy;
            this.maxReceive = maxReceive;
            this.hoverDrain = hoverDrain;
            this.boostDrain = boostDrain;
            this.speedMultiplier = speedMultiplier;
            this.climbMultiplier = climbMultiplier;
            this.lore = lore;
        }

        public String getDisplayName() { return displayName; }
        public int getMaxEnergy() { return maxEnergy; }
        public int getMaxReceive() { return maxReceive; }
        public int getHoverDrain() { return hoverDrain; }
        public int getBoostDrain() { return boostDrain; }
        public float getSpeedMultiplier() { return speedMultiplier; }
        public float getClimbMultiplier() { return climbMultiplier; }
        public String getLore() { return lore; }
    }

    private final BoosterType boosterType;

    public ExoframeFlightBoosterItem(Properties properties, BoosterType boosterType) {
        super(properties.stacksTo(1));
        this.boosterType = boosterType;
    }

    public BoosterType getBoosterType() {
        return boosterType;
    }

    @Override
    public @Nullable ICapabilityProvider initCapabilities(ItemStack stack, @Nullable CompoundTag nbt) {
        return new EnergyCapabilityProvider(stack, boosterType.getMaxEnergy(), boosterType.getMaxReceive(), boosterType.getBoostDrain() * 2);
    }

    public static int getEnergyStored(ItemStack stack) {
        if (stack.isEmpty()) return 0;
        return stack.getCapability(ForgeCapabilities.ENERGY).map(IEnergyStorage::getEnergyStored).orElseGet(() -> {
            CompoundTag tag = stack.getTag();
            return tag != null && tag.contains(ItemEnergyStorage.ENERGY_KEY) ? tag.getInt(ItemEnergyStorage.ENERGY_KEY) : 0;
        });
    }

    public static int getMaxEnergy(ItemStack stack) {
        if (stack.getItem() instanceof ExoframeFlightBoosterItem booster) {
            return booster.getBoosterType().getMaxEnergy();
        }
        return 250000;
    }

    public static boolean consumeFlightEnergy(ItemStack stack, boolean boosting) {
        if (stack.isEmpty() || !(stack.getItem() instanceof ExoframeFlightBoosterItem booster)) return false;
        int drain = boosting ? booster.getBoosterType().getBoostDrain() : booster.getBoosterType().getHoverDrain();
        return stack.getCapability(ForgeCapabilities.ENERGY).map(storage -> {
            if (storage.getEnergyStored() >= drain) {
                storage.extractEnergy(drain, false);
                return true;
            }
            return false;
        }).orElse(false);
    }

    @Override
    public boolean isBarVisible(ItemStack stack) {
        return true;
    }

    @Override
    public int getBarWidth(ItemStack stack) {
        int energy = getEnergyStored(stack);
        int max = getMaxEnergy(stack);
        return Math.round(13.0F * ((float) energy / (float) max));
    }

    @Override
    public int getBarColor(ItemStack stack) {
        float ratio = (float) getEnergyStored(stack) / (float) getMaxEnergy(stack);
        return Mth.hsvToRgb(ratio / 3.0F, 1.0F, 1.0F); // Red -> Yellow -> Green
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("§b▶ Mech Back Module: §f" + boosterType.getDisplayName()));
        tooltip.add(Component.literal("§7" + boosterType.getLore()));

        int energy = getEnergyStored(stack);
        int max = getMaxEnergy(stack);
        int pct = Math.round(100.0F * energy / max);
        ChatFormatting color = pct > 50 ? ChatFormatting.GREEN : pct > 20 ? ChatFormatting.YELLOW : ChatFormatting.RED;
        tooltip.add(Component.literal(String.format("§7⚡ Forge Energy: %s%,d / %,d FE (%d%%)", color, energy, max, pct)));

        tooltip.add(Component.literal("§7Enables Gundam 3D Aerial Free Flight:"));
        tooltip.add(Component.literal("§e • Space (in air)§7: Hover / Rocket Climb (" + boosterType.getHoverDrain() + " FE/t)"));
        tooltip.add(Component.literal("§e • C (Mech Crouch)§7: Descend / Land"));
        tooltip.add(Component.literal("§e • Pitch Down / W§7: Flight Vectoring & Dive"));
        tooltip.add(Component.literal("§6 • Sprint (Ctrl)§7: Supersonic Dash (" + boosterType.getBoostDrain() + " FE/t)"));
        tooltip.add(Component.literal("§7 • Shift§8: Dismount Cockpit"));
        tooltip.add(Component.literal("§8Rechargeable in any Forge Energy (FE) charger."));
    }
}
