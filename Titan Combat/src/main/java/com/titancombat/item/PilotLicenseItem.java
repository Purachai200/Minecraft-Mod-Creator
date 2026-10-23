package com.titancombat.item;

import com.titancombat.entity.BaseTitanEntity;
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

public class PilotLicenseItem extends Item {

    public PilotLicenseItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (target instanceof BaseTitanEntity titan) {
            if (!player.level().isClientSide) {
                if (titan.getOwnerUUID() == null || titan.getOwnerUUID().isEmpty()) {
                    // Claim unowned Titan
                    titan.setOwner(player);
                    player.sendSystemMessage(Component.translatable("message.titancombat.license_bound", titan.getTitanClass().getDisplayName(), player.getName().getString()));
                    player.level().playSound(null, titan.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 1.0F, 1.2F);
                } else if (player.getUUID().toString().equals(titan.getOwnerUUID())) {
                    player.sendSystemMessage(Component.literal("§a[BIOMETRIC VERIFIED] You are the registered pilot of this " + titan.getTitanClass().getDisplayName() + "."));
                } else {
                    player.sendSystemMessage(Component.literal("§c[ACCESS DENIED] Titan is registered to Pilot: " + titan.getOwnerName()));
                }
            }
            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }
        return super.interactLivingEntity(stack, player, target, hand);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("IMC / Militia Certified Pilot License").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.literal("Right-click an unowned Titan to register ownership.").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("Prevents other players from boarding or stealing your Titan.").withStyle(ChatFormatting.AQUA));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
