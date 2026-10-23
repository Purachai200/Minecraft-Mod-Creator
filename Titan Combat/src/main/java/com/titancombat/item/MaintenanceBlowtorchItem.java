package com.titancombat.item;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

public class MaintenanceBlowtorchItem extends Item {

    public MaintenanceBlowtorchItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (target instanceof BaseTitanEntity titan) {
            if (titan.getHealth() < titan.getMaxHealth()) {
                if (!player.level().isClientSide) {
                    titan.heal(15.0F);
                    stack.hurtAndBreak(1, player, (p) -> p.broadcastBreakEvent(hand));
                    player.level().playSound(null, titan.blockPosition(), SoundEvents.FIRE_EXTINGUISH, SoundSource.PLAYERS, 0.8F, 1.6F);
                    player.sendSystemMessage(Component.translatable("message.titancombat.hull_welded", (int) titan.getHealth(), (int) titan.getMaxHealth()));
                } else {
                    for (int i = 0; i < 6; i++) {
                        player.level().addParticle(ParticleTypes.FLAME,
                                titan.getX() + (player.level().random.nextDouble() - 0.5D) * 1.0D,
                                titan.getY() + 1.2D + player.level().random.nextDouble() * 1.5D,
                                titan.getZ() + (player.level().random.nextDouble() - 0.5D) * 1.0D,
                                0, 0.05D, 0);
                        player.level().addParticle(ParticleTypes.SMOKE,
                                titan.getX() + (player.level().random.nextDouble() - 0.5D) * 1.0D,
                                titan.getY() + 1.5D + player.level().random.nextDouble() * 1.5D,
                                titan.getZ() + (player.level().random.nextDouble() - 0.5D) * 1.0D,
                                0, 0.1D, 0);
                    }
                }
                return InteractionResult.sidedSuccess(player.level().isClientSide);
            }
        }
        return super.interactLivingEntity(stack, player, target, hand);
    }
}
