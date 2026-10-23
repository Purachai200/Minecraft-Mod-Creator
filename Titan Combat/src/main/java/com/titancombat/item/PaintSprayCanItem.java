package com.titancombat.item;

import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.MechFaction;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

public class PaintSprayCanItem extends Item {

    public PaintSprayCanItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (target instanceof BaseMechEntity mech) {
            if (!player.level().isClientSide) {
                int currentFactionId = mech.getFactionId();
                MechFaction[] factions = MechFaction.values();
                int nextIndex = (currentFactionId + (player.isShiftKeyDown() ? -1 : 1) + factions.length) % factions.length;
                MechFaction nextFaction = factions[nextIndex];

                mech.setFaction(nextFaction);

                player.sendSystemMessage(Component.translatable("message.titancombat.faction_switched", nextFaction.getDisplayName()));
                player.level().playSound(null, mech.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 0.8F, 1.6F);
            }
            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }
        return super.interactLivingEntity(stack, player, target, hand);
    }
}
