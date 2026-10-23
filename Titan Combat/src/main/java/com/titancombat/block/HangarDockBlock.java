package com.titancombat.block;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.List;

public class HangarDockBlock extends Block {
    private static final VoxelShape SHAPE = Block.box(0, 0, 0, 16, 4, 16);

    public HangarDockBlock(Properties properties) {
        super(properties);
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        super.stepOn(level, pos, state, entity);

        if (entity instanceof BaseTitanEntity titan) {
            // Snap gently to center of dock
            double targetX = pos.getX() + 0.5D;
            double targetZ = pos.getZ() + 0.5D;

            if (titan.distanceToSqr(targetX, titan.getY(), targetZ) < 1.8D) {
                if (!titan.isVehicle() && !titan.isStandbyMode()) {
                    titan.setStandbyMode(true);
                    if (!level.isClientSide) {
                        level.playSound(null, pos, SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 1.0F, 0.8F);
                    }
                }

                // Hangar automated maintenance & trickle charging
                if (!level.isClientSide && titan.tickCount % 20 == 0) {
                    if (titan.getHealth() < titan.getMaxHealth()) {
                        titan.heal(1.0F);
                    }
                    if (titan.getShield() < titan.getMaxShield()) {
                        titan.setShield(titan.getShield() + 2.0F);
                    }
                }

                if (level.isClientSide && level.random.nextFloat() < 0.2F) {
                    level.addParticle(ParticleTypes.ELECTRIC_SPARK,
                            targetX + (level.random.nextDouble() - 0.5D) * 1.5D,
                            pos.getY() + 0.4D,
                            targetZ + (level.random.nextDouble() - 0.5D) * 1.5D,
                            0, 0.05D, 0);
                }
            }
        }
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (!level.isClientSide) {
            AABB searchArea = new AABB(pos).inflate(2.0D, 4.0D, 2.0D);
            List<BaseTitanEntity> titans = level.getEntitiesOfClass(BaseTitanEntity.class, searchArea);

            if (!titans.isEmpty()) {
                BaseTitanEntity titan = titans.get(0);
                String owner = titan.getOwnerName().isEmpty() ? "Unregistered" : titan.getOwnerName();
                player.sendSystemMessage(Component.literal("§6=== HANGAR DOCK STATUS ==="));
                player.sendSystemMessage(Component.literal("§eStationed Titan: §f" + titan.getTitanClass().getDisplayName()));
                player.sendSystemMessage(Component.literal("§eRegistered Pilot: §f" + owner));
                player.sendSystemMessage(Component.literal("§eHull Integrity: §f" + (int) titan.getHealth() + " / " + (int) titan.getMaxHealth()));
                player.sendSystemMessage(Component.literal("§eOvershield: §f" + (int) titan.getShield() + " / " + (int) titan.getMaxShield()));
                player.sendSystemMessage(Component.literal("§aStatus: DOCKED & STANDBY (Hatch Open)"));
            } else {
                player.sendSystemMessage(Component.literal("§7[Hangar Dock] No Titan currently docked. Walk a Titan onto this pad to anchor it."));
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
