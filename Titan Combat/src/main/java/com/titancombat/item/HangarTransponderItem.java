package com.titancombat.item;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class HangarTransponderItem extends Item {
    public static final double MAX_RADIO_RANGE = 64.0D;

    public HangarTransponderItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (target instanceof BaseTitanEntity titan) {
            Level level = player.level();
            if (!level.isClientSide) {
                // Link Remote Key Fob to this Titan
                CompoundTag tag = stack.getOrCreateTag();
                tag.putUUID("TitanUUID", titan.getUUID());
                tag.putString("TitanName", titan.getTitanClass().getDisplayName());

                player.sendSystemMessage(Component.translatable("message.titancombat.transponder_linked",
                        titan.getTitanClass().getDisplayName(), titan.blockPosition().getX(), titan.blockPosition().getZ()));
                level.playSound(null, player.blockPosition(), SoundEvents.NOTE_BLOCK_CHIME.get(), SoundSource.PLAYERS, 1.0F, 1.8F);
                return InteractionResult.SUCCESS;
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        return super.interactLivingEntity(stack, player, target, hand);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);

        if (!level.isClientSide) {
            CompoundTag tag = stack.getTag();
            if (tag == null || !tag.contains("TitanUUID")) {
                player.sendSystemMessage(Component.literal("§c[KEY FOB ERROR] Remote not linked to any Mech! Right-click your Mech first."));
                return InteractionResultHolder.fail(stack);
            }

            java.util.UUID titanUUID = tag.getUUID("TitanUUID");
            if (level instanceof net.minecraft.server.level.ServerLevel serverLevel) {
                net.minecraft.world.entity.Entity entity = serverLevel.getEntity(titanUUID);

                if (entity instanceof BaseTitanEntity titan) {
                    double distance = player.distanceTo(titan);

                    // Range Check (Max 64 meters)
                    if (distance > MAX_RADIO_RANGE) {
                        player.sendSystemMessage(Component.literal("§c[OUT OF RANGE] Mech signal out of range! Distance: " + (int) distance + "m (Max: 64m). Return closer to your Mech."));
                        level.playSound(null, player.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.6F);
                        return InteractionResultHolder.fail(stack);
                    }

                    // Within Range: Toggle Remote Standby / Navigation
                    boolean currentStandby = titan.isStandbyMode();
                    titan.setStandbyMode(!currentStandby);

                    if (currentStandby) {
                        // Power up & move toward player
                        titan.getNavigation().moveTo(player, 1.2D);
                        player.sendSystemMessage(Component.literal("§a[REMOTE SIGNAL] " + titan.getTitanClass().getDisplayName() + " engines engaged. Advancing toward pilot."));
                        level.playSound(null, player.blockPosition(), SoundEvents.NOTE_BLOCK_BELL.get(), SoundSource.PLAYERS, 1.2F, 1.5F);
                    } else {
                        // Park / Standby
                        titan.getNavigation().stop();
                        player.sendSystemMessage(Component.literal("§6[REMOTE SIGNAL] " + titan.getTitanClass().getDisplayName() + " anchored in Standby Mode."));
                        level.playSound(null, player.blockPosition(), SoundEvents.NOTE_BLOCK_BELL.get(), SoundSource.PLAYERS, 1.2F, 0.8F);
                    }
                    return InteractionResultHolder.success(stack);
                } else {
                    player.sendSystemMessage(Component.literal("§c[SIGNAL LOST] Could not locate Mech. Ensure its chunk is loaded or re-link."));
                }
            }
        }

        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        CompoundTag tag = stack.getTag();
        if (tag != null && tag.contains("TitanName")) {
            tooltip.add(Component.literal("Linked Mech: ").withStyle(ChatFormatting.GRAY)
                    .append(Component.literal(tag.getString("TitanName")).withStyle(ChatFormatting.GOLD)));
        } else {
            tooltip.add(Component.literal("No Mech linked. Right-click your Mech to pair.").withStyle(ChatFormatting.DARK_GRAY));
        }
        tooltip.add(Component.literal("Right-click air (Max 64m): ").withStyle(ChatFormatting.YELLOW)
                .append(Component.literal("Remote Toggle Engine / Call Mech to You").withStyle(ChatFormatting.WHITE)));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
