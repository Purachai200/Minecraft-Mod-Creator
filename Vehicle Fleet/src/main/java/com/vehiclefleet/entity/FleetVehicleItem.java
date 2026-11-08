package com.vehiclefleet.entity;

import com.vehiclefleet.FleetVehicles;
import com.vehiclefleet.VehicleFleetMod;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** Deployer item: right-click a block or a water surface to place the vehicle. */
public class FleetVehicleItem extends Item {
    private final FleetVehicles.Spec spec;

    public FleetVehicleItem(FleetVehicles.Spec spec, Properties props) {
        super(props);
        this.spec = spec;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        BlockHitResult hit = getPlayerPOVHitResult(level, player, ClipContext.Fluid.SOURCE_ONLY);
        if (hit.getType() != HitResult.Type.BLOCK) return InteractionResultHolder.pass(stack);
        if (!level.isClientSide) {
            FleetVehicleEntity e = VehicleFleetMod.TYPES.get(spec.id).get().create(level);
            if (e == null) return InteractionResultHolder.fail(stack);
            double y = hit.getLocation().y + (level.getFluidState(hit.getBlockPos()).isEmpty() ? 0.05D : 0.0D);
            e.moveTo(hit.getLocation().x, y, hit.getLocation().z, player.getYRot(), 0.0F);
            level.addFreshEntity(e);
            if (!player.getAbilities().instabuild) stack.shrink(1);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Tier " + spec.tier + " - " + spec.payload));
    }
}
