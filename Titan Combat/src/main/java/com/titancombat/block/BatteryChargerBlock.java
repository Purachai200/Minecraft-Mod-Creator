package com.titancombat.block;

import com.titancombat.block.entity.BatteryChargerBlockEntity;
import com.titancombat.block.entity.ModBlockEntities;
import com.titancombat.item.TitanBatteryItem;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

public class BatteryChargerBlock extends BaseEntityBlock {
    public static final DirectionProperty FACING = HorizontalDirectionalBlock.FACING;
    private static final VoxelShape SHAPE = Block.box(1, 0, 1, 15, 14, 15);

    public BatteryChargerBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(FACING, Direction.NORTH));
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return this.defaultBlockState().setValue(FACING, context.getHorizontalDirection().getOpposite());
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING);
    }

    @Override
    public RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new BatteryChargerBlockEntity(pos, state);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, net.minecraft.util.RandomSource random) {
        BlockEntity be = level.getBlockEntity(pos);
        if (be instanceof BatteryChargerBlockEntity charger && charger.getEnergyStored() > 0) {
            if (random.nextFloat() < 0.4F) {
                double x = pos.getX() + 0.5D + (random.nextDouble() - 0.5D) * 0.4D;
                double y = pos.getY() + 0.85D;
                double z = pos.getZ() + 0.5D + (random.nextDouble() - 0.5D) * 0.4D;
                level.addParticle(net.minecraft.core.particles.ParticleTypes.ELECTRIC_SPARK, x, y, z, 0.0D, 0.04D, 0.0D);
            }
        }
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> blockEntityType) {
        if (level.isClientSide) return null;
        return createTickerHelper(blockEntityType, ModBlockEntities.BATTERY_CHARGER.get(), BatteryChargerBlockEntity::serverTick);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide) return InteractionResult.SUCCESS;

        BlockEntity be = level.getBlockEntity(pos);
        if (!(be instanceof BatteryChargerBlockEntity charger)) return InteractionResult.PASS;

        ItemStack held = player.getItemInHand(hand);

        // 1. Insert Battery (Empty or Partially Charged)
        if (held.getItem() instanceof TitanBatteryItem) {
            if (charger.getBatterySlot().isEmpty()) {
                int heldEnergy = TitanBatteryItem.getEnergy(held);
                int heldCapacity = TitanBatteryItem.getCapacity(held);
                if (heldEnergy >= heldCapacity) {
                    player.sendSystemMessage(Component.translatable("message.titancombat.battery_already_full"));
                    return InteractionResult.CONSUME;
                }
                charger.setBatterySlot(held.split(1));
                level.playSound(null, pos, SoundEvents.IRON_DOOR_CLOSE, SoundSource.BLOCKS, 1.0F, 1.4F);
                player.sendSystemMessage(Component.translatable("message.titancombat.battery_inserted_charger_energy",
                        String.format("%,d", heldEnergy), String.format("%,d", heldCapacity)));
                return InteractionResult.SUCCESS;
            }
        }

        // 2. Feed Solid Fuel directly for Standby Charging
        int fuelFe = getFuelEnergy(held);
        if (fuelFe > 0) {
            if (charger.getEnergyStored() < charger.getMaxEnergyStored()) {
                charger.addEnergy(fuelFe);
                if (held.is(Items.LAVA_BUCKET)) {
                    if (!player.getAbilities().instabuild) {
                        player.setItemInHand(hand, new ItemStack(Items.BUCKET));
                    }
                } else {
                    if (!player.getAbilities().instabuild) {
                        held.shrink(1);
                    }
                }
                level.playSound(null, pos, SoundEvents.FURNACE_FIRE_CRACKLE, SoundSource.BLOCKS, 1.2F, 1.0F);
                player.sendSystemMessage(Component.translatable("message.titancombat.battery_charger_fuel", fuelFe, charger.getEnergyStored(), charger.getMaxEnergyStored()));
                return InteractionResult.SUCCESS;
            } else {
                player.sendSystemMessage(Component.literal("§e[CHARGER] Internal energy capacity is full (" + charger.getMaxEnergyStored() + " FE)."));
                return InteractionResult.CONSUME;
            }
        }

        // 3. Extract Battery (if slot is not empty)
        if (!charger.getBatterySlot().isEmpty()) {
            ItemStack extracted = charger.getBatterySlot().copy();
            charger.setBatterySlot(ItemStack.EMPTY);
            int extractedEnergy = TitanBatteryItem.getEnergy(extracted);
            int extractedCap = TitanBatteryItem.getCapacity(extracted);
            if (!player.getInventory().add(extracted)) {
                player.drop(extracted, false);
            }
            level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 1.0F, 1.0F);
            player.sendSystemMessage(Component.translatable("message.titancombat.battery_extracted_charger_energy",
                    String.format("%,d", extractedEnergy), String.format("%,d", extractedCap)));
            return InteractionResult.SUCCESS;
        }

        // 4. Query Status
        String batteryStatus = "§7[None]";
        if (!charger.getBatterySlot().isEmpty()) {
            int cur = TitanBatteryItem.getEnergy(charger.getBatterySlot());
            int cap = TitanBatteryItem.getCapacity(charger.getBatterySlot());
            int pct = Math.round((float) cur * 100.0F / (float) Math.max(1, cap));
            if (cur >= cap) {
                batteryStatus = "§aFully Charged (" + String.format("%,d", cur) + " / " + String.format("%,d", cap) + " FE)";
            } else {
                batteryStatus = "§eCharging " + pct + "% (" + String.format("%,d", cur) + " / " + String.format("%,d", cap) + " FE)";
            }
        }
        player.sendSystemMessage(Component.translatable("message.titancombat.battery_charger_status",
                charger.getEnergyStored(), charger.getMaxEnergyStored(), batteryStatus));
        return InteractionResult.SUCCESS;
    }

    private int getFuelEnergy(ItemStack stack) {
        if (stack.is(Items.COAL) || stack.is(Items.CHARCOAL)) return 2500;
        if (stack.is(Items.REDSTONE)) return 1000;
        if (stack.is(Items.REDSTONE_BLOCK)) return 9000;
        if (stack.is(Items.BLAZE_ROD)) return 5000;
        if (stack.is(Items.COAL_BLOCK)) return 22500;
        if (stack.is(Items.LAVA_BUCKET)) return 20000;
        return 0;
    }

    @Override
    public void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean isMoving) {
        if (!state.is(newState.getBlock())) {
            BlockEntity be = level.getBlockEntity(pos);
            if (be instanceof BatteryChargerBlockEntity charger && !charger.getBatterySlot().isEmpty()) {
                Containers.dropItemStack(level, pos.getX(), pos.getY(), pos.getZ(), charger.getBatterySlot());
            }
            super.onRemove(state, level, pos, newState, isMoving);
        }
    }
}
