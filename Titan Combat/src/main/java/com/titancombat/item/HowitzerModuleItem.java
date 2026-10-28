package com.titancombat.item;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.gui.TitanMenu;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
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

/** M-120 howitzer back module: goes in the back equipment slot (instead of a flight module). */
public class HowitzerModuleItem extends Item {
    public HowitzerModuleItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (!(target instanceof BaseTitanEntity titan)) return super.interactLivingEntity(stack, player, target, hand);
        if (!player.level().isClientSide) {
            ItemStack old = titan.getTitanInventory().getItem(TitanMenu.FLIGHT_SLOT);
            titan.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT, stack.split(1));
            player.level().playSound(null, titan.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE, SoundSource.PLAYERS, 1.6F, 0.8F);
            if (!player.getAbilities().instabuild && !old.isEmpty() && !player.getInventory().add(old)) player.drop(old, false);
            player.sendSystemMessage(Component.translatable("message.titancombat.howitzer_installed", titan.getTitanClass().getDisplayName()));
        }
        return InteractionResult.sidedSuccess(player.level().isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.titancombat.howitzer.desc").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.titancombat.howitzer.keys").withStyle(ChatFormatting.DARK_AQUA));
    }
}
