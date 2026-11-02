package com.titancombat.item;

import com.titancombat.entity.TitanArmorTheme;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class TitanArmorItem extends Item {
    public enum ArmorSlot {
        HEAD("head", 4.0F, 10.0F),
        CHEST("chest", 10.0F, 25.0F),
        ARMS("arms", 6.0F, 15.0F),
        LEGS("legs", 8.0F, 20.0F);

        private final String id;
        private final float armorBonus;
        private final float shieldBonus;

        ArmorSlot(String id, float armorBonus, float shieldBonus) {
            this.id = id;
            this.armorBonus = armorBonus;
            this.shieldBonus = shieldBonus;
        }

        public String getId() {
            return id;
        }

        public float getArmorBonus() {
            return armorBonus;
        }

        public float getShieldBonus() {
            return shieldBonus;
        }
    }

    private final ArmorSlot slot;

    public TitanArmorItem(ArmorSlot slot, Properties properties) {
        super(properties.stacksTo(4).rarity(Rarity.RARE));
        this.slot = slot;
    }

    public ArmorSlot getArmorSlot() {
        return slot;
    }

    @Override
    public Component getName(ItemStack stack) {
        TitanArmorTheme theme = getTheme(stack);
        return Component.translatable(this.getDescriptionId(stack))
                .append(" (")
                .append(Component.literal(theme.getDisplayName()))
                .append(")");
    }

    public static TitanArmorTheme getTheme(ItemStack stack) {
        CompoundTag tag = stack.getTag();
        if (tag != null && tag.contains("ArmorTheme")) {
            return TitanArmorTheme.byId(tag.getInt("ArmorTheme"));
        }
        return TitanArmorTheme.VANGUARD;
    }

    public static void setTheme(ItemStack stack, TitanArmorTheme theme) {
        stack.getOrCreateTag().putInt("ArmorTheme", theme.getId());
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.isShiftKeyDown()) {
            if (!level.isClientSide) {
                TitanArmorTheme current = getTheme(stack);
                int nextId = (current.getId() + 1) % TitanArmorTheme.values().length;
                TitanArmorTheme nextTheme = TitanArmorTheme.byId(nextId);
                setTheme(stack, nextTheme);

                player.sendSystemMessage(Component.translatable("message.titancombat.theme_switched",
                        nextTheme.getDisplayName(), nextTheme.getDescription()));
                level.playSound(null, player.blockPosition(), SoundEvents.ARMOR_EQUIP_IRON, SoundSource.PLAYERS, 0.8F, 1.2F);
            }
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        }
        return super.use(level, player, hand);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        TitanArmorTheme theme = getTheme(stack);
        tooltip.add(Component.literal("Slot: ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal(slot.getId().toUpperCase()).withStyle(ChatFormatting.GOLD)));
        tooltip.add(Component.literal("Theme (17 Variants): ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal(theme.getDisplayName()).withStyle(ChatFormatting.AQUA)));
        tooltip.add(Component.literal(theme.getDescription()).withStyle(ChatFormatting.DARK_GRAY));
        tooltip.add(Component.literal("Armor Protection: +").withStyle(ChatFormatting.GREEN)
                .append(Component.literal(String.format("%.1f", slot.getArmorBonus() + theme.getArmorValue() * 0.25F))));
        tooltip.add(Component.literal("Shift + Right-Click in air: ").withStyle(ChatFormatting.DARK_AQUA)
                .append(Component.literal("Cycle Armor Theme (17 Styles)").withStyle(ChatFormatting.YELLOW)));
    }
}
