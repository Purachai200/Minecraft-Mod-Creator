package com.titancombat.item;

import com.titancombat.entity.BaseMechEntity;
import com.titancombat.sound.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

public class TitanBatteryItem extends Item {

    public TitanBatteryItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (target instanceof BaseMechEntity mech) {
            if (!player.level().isClientSide) {
                // Restore Energy & Shield to 100%
                mech.setShield(mech.getMaxShield());
                mech.setDashCharge(100.0F);

                player.level().playSound(null, mech.blockPosition(), ModSounds.TITAN_GET_BATTERY.get(), SoundSource.PLAYERS, 1.2F, 1.0F);

                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                    ItemStack empty = new ItemStack(ModItems.EMPTY_BATTERY.get());
                    if (!player.getInventory().add(empty)) {
                        player.drop(empty, false);
                    }
                }

                player.sendSystemMessage(Component.translatable("message.titancombat.battery_inserted"));
            } else {
                for (int i = 0; i < 15; i++) {
                    player.level().addParticle(ParticleTypes.ELECTRIC_SPARK,
                            mech.getX() + (player.level().random.nextDouble() - 0.5D) * 1.5D,
                            mech.getY() + 2.0D + player.level().random.nextDouble() * 1.5D,
                            mech.getZ() + (player.level().random.nextDouble() - 0.5D) * 1.5D,
                            0, 0.1D, 0);
                }
            }
            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }
        return super.interactLivingEntity(stack, player, target, hand);
    }
}
