package com.titancombat.item;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanFlightModule;
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

public class TitanFlightModuleItem extends Item {
    private final TitanFlightModule module;

    public TitanFlightModuleItem(TitanFlightModule module, Properties properties) {
        super(properties);
        this.module = module;
    }

    public TitanFlightModule getModule() {
        return module;
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (target instanceof BaseTitanEntity titan) {
            if (!player.level().isClientSide) {
                TitanFlightModule oldModule = titan.getFlightModule();
                titan.setFlightModule(this.module);
                player.level().playSound(null, titan.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE, SoundSource.PLAYERS, 1.6F, 1.0F);

                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                    if (oldModule != TitanFlightModule.NONE) {
                        ItemStack oldStack = new ItemStack(ModItems.FLIGHT_MODULES.get(oldModule).get());
                        if (!player.getInventory().add(oldStack)) {
                            player.drop(oldStack, false);
                        }
                    }
                }

                player.sendSystemMessage(Component.translatable("message.titancombat.flight_module_installed",
                        this.module.getDisplayName(), titan.getTitanClass().getDisplayName()));
            }
            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }
        return super.interactLivingEntity(stack, player, target, hand);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.titancombat.flight_module.desc").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("§b• " + module.getDisplayName()));
        tooltip.add(Component.literal(String.format("§7Vertical Lift: §a+%.2f §7| Cruise Speed: §e%.0f%%",
                module.getVerticalLift(), module.getForwardMultiplier() * 100.0F)));
        tooltip.add(Component.literal(String.format("§7Ceiling: §6%.0f blocks §7| Fuel Drain: §c%.2f/t",
                module.getMaxFlightCeiling(), module.getEnergyDrain())));
        tooltip.add(Component.translatable("tooltip.titancombat.flight_module.equip_hint").withStyle(ChatFormatting.DARK_AQUA));
    }
}
