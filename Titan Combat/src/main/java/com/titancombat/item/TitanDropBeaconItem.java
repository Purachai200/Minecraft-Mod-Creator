package com.titancombat.item;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.MechFaction;
import com.titancombat.entity.MechState;
import com.titancombat.entity.ModEntities;
import com.titancombat.entity.TitanClass;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class TitanDropBeaconItem extends Item {

    public TitanDropBeaconItem(Properties properties) {
        super(properties);
    }

    public static TitanClass getSelectedTitan(ItemStack stack) {
        CompoundTag tag = stack.getTag();
        if (tag != null && tag.contains("SelectedTitan")) {
            return TitanClass.byId(tag.getString("SelectedTitan"));
        }
        return TitanClass.ION;
    }

    public static void setSelectedTitan(ItemStack stack, TitanClass titanClass) {
        stack.getOrCreateTag().putString("SelectedTitan", titanClass.getId());
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.isShiftKeyDown()) {
            if (!level.isClientSide) {
                TitanClass current = getSelectedTitan(stack);
                TitanClass[] values = TitanClass.values();
                int nextIndex = (current.ordinal() + 1) % values.length;
                TitanClass next = values[nextIndex];
                setSelectedTitan(stack, next);

                player.sendSystemMessage(Component.translatable("message.titancombat.beacon_switched", next.getDisplayName(), next.getRole()));
                level.playSound(null, player.blockPosition(), SoundEvents.UI_BUTTON_CLICK.get(), SoundSource.PLAYERS, 0.8F, 1.4F);
            }
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        }
        return super.use(level, player, hand);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos().above();
        Player player = context.getPlayer();
        ItemStack stack = context.getItemInHand();

        if (!level.isClientSide) {
            TitanClass selected = getSelectedTitan(stack);
            EntityType<? extends BaseTitanEntity> type = switch (selected) {
                case SCORCH -> ModEntities.SCORCH_TITAN.get();
                case RONIN -> ModEntities.RONIN_TITAN.get();
                case TONE -> ModEntities.TONE_TITAN.get();
                case LEGION -> ModEntities.LEGION_TITAN.get();
                case MONARCH -> ModEntities.MONARCH_TITAN.get();
                case NORTHSTAR -> ModEntities.NORTHSTAR_TITAN.get();
                default -> ModEntities.ION_TITAN.get();
            };

            BaseTitanEntity titan = type.create(level);
            if (titan != null) {
                // Deploy directly onto the ground (Grounded Mech Deployment)
                titan.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, player != null ? player.getYRot() : 0, 0);
                titan.setMechState(MechState.IDLE);
                titan.setStandbyMode(false); // Stand tall in full combat-ready posture
                if (player != null) {
                    titan.setOwner(player);
                }
                titan.setFaction(MechFaction.APEX_VANGUARD);
                level.addFreshEntity(titan);

                level.playSound(null, pos, com.titancombat.sound.ModSounds.TITAN_STEP.get(), SoundSource.PLAYERS, 2.0F, 0.8F);
                level.playSound(null, pos, com.titancombat.sound.ModSounds.TITAN_CABIN_ENTER.get(), SoundSource.PLAYERS, 1.6F, 1.0F);
                if (player != null) {
                    player.sendSystemMessage(Component.literal("§a[DEPLOYMENT SUCCESS] " + selected.getDisplayName() + " deployed on ground. Cockpit hatch opened for embarkation."));
                }

                if (player != null && !player.getAbilities().instabuild) {
                    stack.shrink(1);
                }
            }
        } else {
            for (int i = 0; i < 15; i++) {
                level.addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE,
                        pos.getX() + 0.5D + (level.random.nextDouble() - 0.5D) * 1.0D,
                        pos.getY() + 0.2D + level.random.nextDouble() * 0.5D,
                        pos.getZ() + 0.5D + (level.random.nextDouble() - 0.5D) * 1.0D,
                        0, 0.05D, 0);
            }
        }

        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        TitanClass selected = getSelectedTitan(stack);
        tooltip.add(Component.literal("Selected Mech: ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal(selected.getDisplayName() + " (" + selected.getRole() + ")").withStyle(ChatFormatting.GOLD)));
        tooltip.add(Component.literal("Right-click ground: ").withStyle(ChatFormatting.GREEN)
                .append(Component.literal("Assemble & Deploy on Ground").withStyle(ChatFormatting.WHITE)));
        tooltip.add(Component.literal("Shift + Right-Click in air: ").withStyle(ChatFormatting.DARK_AQUA)
                .append(Component.literal("Switch Mech Class").withStyle(ChatFormatting.YELLOW)));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
