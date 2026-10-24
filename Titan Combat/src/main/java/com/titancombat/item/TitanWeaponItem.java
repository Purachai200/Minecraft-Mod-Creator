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

/** A titan weapon module: install it in the cockpit bay's weapon slot to arm any chassis with it. */
public class TitanWeaponItem extends Item {
    private final TitanWeapon weapon;

    public TitanWeaponItem(TitanWeapon weapon, Properties properties) {
        super(properties);
        this.weapon = weapon;
    }

    public TitanWeapon getWeapon() {
        return weapon;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.titancombat.weapon.install").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.titancombat.weapon.stats",
                weapon.getMagazineSize(), String.format("%.1f", weapon.getReloadTicks() / 20.0F),
                Math.round(weapon.getDamage() * weapon.getPellets()), Math.round(1200.0F / weapon.getCooldownTicks()))
                .withStyle(ChatFormatting.DARK_AQUA));
        tooltip.add(Component.translatable("tooltip.titancombat.weapon.ammo",
                Component.translatable("item.titancombat.ammo_" + weapon.getId())).withStyle(ChatFormatting.GOLD));
    }
}
