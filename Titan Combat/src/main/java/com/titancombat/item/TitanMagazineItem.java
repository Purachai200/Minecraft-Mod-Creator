package com.titancombat.item;

import com.titancombat.entity.TitanWeapon;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** One full magazine for a specific titan weapon. Reloading consumes one. */
public class TitanMagazineItem extends Item {
    private final TitanWeapon weapon;

    public TitanMagazineItem(TitanWeapon weapon, Properties properties) {
        super(properties);
        this.weapon = weapon;
    }

    public TitanWeapon getWeapon() {
        return weapon;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.titancombat.magazine",
                weapon.getMagazineSize(), Component.translatable(weapon.getTranslationKey())).withStyle(ChatFormatting.GRAY));
    }
}
