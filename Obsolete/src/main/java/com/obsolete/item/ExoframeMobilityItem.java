package com.obsolete.item;

import com.obsolete.energy.EnergyCapabilityProvider;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
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
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** FE-powered mobility equipment: the heel roller dash pods (UTILITY) and the hydro-jet propulsor (BACK). */
public class ExoframeMobilityItem extends Item {

    public enum Kind {
        ROLLER_DASH(ExoframeArmorSlot.UTILITY, 120000, 1500, 30),
        HYDRO_JET(ExoframeArmorSlot.BACK, 150000, 1500, 20);

        public final ExoframeArmorSlot slot;
        public final int maxEnergy;
        public final int maxReceive;
        /** FE per tick while the drive is running. */
        public final int drain;

        Kind(ExoframeArmorSlot slot, int maxEnergy, int maxReceive, int drain) {
            this.slot = slot;
            this.maxEnergy = maxEnergy;
            this.maxReceive = maxReceive;
            this.drain = drain;
        }
    }

    private final Kind kind;

    public ExoframeMobilityItem(Properties properties, Kind kind) {
        super(properties.stacksTo(1));
        this.kind = kind;
    }

    public Kind getKind() {
        return kind;
    }

    @Override
    public @Nullable ICapabilityProvider initCapabilities(ItemStack stack, @Nullable CompoundTag nbt) {
        return new EnergyCapabilityProvider(stack, kind.maxEnergy, kind.maxReceive, kind.drain * 2);
    }

    public static int getEnergy(ItemStack stack) {
        return stack.getCapability(ForgeCapabilities.ENERGY).map(e -> e.getEnergyStored()).orElse(0);
    }

    /** Drains one tick of drive power; false when the cell is flat. */
    public static boolean drain(ItemStack stack) {
        if (!(stack.getItem() instanceof ExoframeMobilityItem m)) return false;
        return stack.getCapability(ForgeCapabilities.ENERGY).map(e -> {
            if (e.getEnergyStored() < m.kind.drain) return false;
            e.extractEnergy(m.kind.drain, false);
            return true;
        }).orElse(false);
    }

    @Override
    public boolean isBarVisible(ItemStack stack) {
        return true;
    }

    @Override
    public int getBarWidth(ItemStack stack) {
        return Math.round(13.0F * getEnergy(stack) / kind.maxEnergy);
    }

    @Override
    public int getBarColor(ItemStack stack) {
        return Mth.hsvToRgb((float) getEnergy(stack) / kind.maxEnergy / 3.0F, 1.0F, 1.0F);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        String id = kind == Kind.ROLLER_DASH ? "roller_dash" : "hydro_jet";
        tooltip.add(Component.translatable("tooltip.obsolete.armor_slot", kind.slot.getName().toUpperCase()).withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("tooltip.obsolete." + id + ".usage").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal(String.format("FE: %,d / %,d  (%d FE/t)", getEnergy(stack), kind.maxEnergy, kind.drain))
                .withStyle(ChatFormatting.AQUA));
    }
}
