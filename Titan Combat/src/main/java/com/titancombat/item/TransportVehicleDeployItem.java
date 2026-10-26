package com.titancombat.item;

import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.function.Supplier;

public class TransportVehicleDeployItem extends Item {
    private final Supplier<? extends EntityType<? extends BaseTransportVehicleEntity>> entityTypeSupplier;
    private final String vehicleName;

    public TransportVehicleDeployItem(Supplier<? extends EntityType<? extends BaseTransportVehicleEntity>> entityTypeSupplier, String vehicleName, Properties properties) {
        super(properties);
        this.entityTypeSupplier = entityTypeSupplier;
        this.vehicleName = vehicleName;
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos().above();
        Player player = context.getPlayer();
        ItemStack stack = context.getItemInHand();

        if (!level.isClientSide) {
            EntityType<? extends BaseTransportVehicleEntity> type = entityTypeSupplier.get();
            BaseTransportVehicleEntity vehicle = type.create(level);
            if (vehicle != null) {
                float yaw = player != null ? player.getYRot() : 0.0F;
                vehicle.moveTo(pos.getX() + 0.5D, pos.getY(), pos.getZ() + 0.5D, yaw, 0.0F);
                level.addFreshEntity(vehicle);

                level.playSound(null, pos, SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 1.5F, 0.8F);
                level.playSound(null, pos, SoundEvents.IRON_DOOR_OPEN, SoundSource.PLAYERS, 1.2F, 0.9F);

                if (player != null) {
                    player.sendSystemMessage(Component.literal("§a[DEPLOYED] " + vehicleName + " ready for heavy logistics operation."));
                    if (!player.getAbilities().instabuild) {
                        stack.shrink(1);
                    }
                }
                return InteractionResult.SUCCESS;
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Strategic Logistics Transport Vehicle").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.literal("Right-click ground / water to assemble and deploy.").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("Can haul heavy combat Titans at high travel speeds.").withStyle(ChatFormatting.AQUA));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
