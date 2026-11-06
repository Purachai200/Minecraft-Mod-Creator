package com.titancombat.item;

import com.titancombat.entity.TitanClass;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** Modular Titan Frame Beacon: deploys dedicated frame or cycles across 6 frame variants. */
public class TitanFrameBeaconItem extends TitanDropBeaconItem {
    @Nullable
    private final TitanClass fixedClass;

    private static final TitanClass[] FRAME_CYCLE = new TitanClass[]{
            TitanClass.STRIKER_FRAME,
            TitanClass.VANGUARD_FRAME,
            TitanClass.COLOSSUS_FRAME,
            TitanClass.TERRAIN_FRAME,
            TitanClass.CYCLOPS_FRAME,
            TitanClass.SPIDER_FRAME
    };

    public TitanFrameBeaconItem(Properties properties) {
        this(null, properties);
    }

    public TitanFrameBeaconItem(@Nullable TitanClass fixedClass, Properties properties) {
        super(properties);
        this.fixedClass = fixedClass;
    }

    @Override
    protected TitanClass selectedTitan(ItemStack stack) {
        if (this.fixedClass != null) {
            return this.fixedClass;
        }
        TitanClass c = getSelectedTitan(stack);
        for (TitanClass frame : FRAME_CYCLE) {
            if (c == frame) return c;
        }
        return TitanClass.STRIKER_FRAME;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (this.fixedClass != null) {
            return super.use(level, player, hand);
        }
        if (!player.isShiftKeyDown()) return InteractionResultHolder.pass(stack);
        if (!level.isClientSide) {
            TitanClass cur = selectedTitan(stack);
            int nextIdx = 0;
            for (int i = 0; i < FRAME_CYCLE.length; i++) {
                if (FRAME_CYCLE[i] == cur) {
                    nextIdx = (i + 1) % FRAME_CYCLE.length;
                    break;
                }
            }
            TitanClass next = FRAME_CYCLE[nextIdx];
            setSelectedTitan(stack, next);
            player.sendSystemMessage(Component.translatable("message.titancombat.beacon_switched", next.getDisplayName(), next.getRole()));
            level.playSound(null, player.blockPosition(), SoundEvents.UI_BUTTON_CLICK.get(), SoundSource.PLAYERS, 0.8F, 1.4F);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Deploys: ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal(selectedTitan(stack).getDisplayName() + " (" + selectedTitan(stack).getRole() + ")").withStyle(ChatFormatting.GOLD)));
        tooltip.add(Component.literal("Right-click ground: ").withStyle(ChatFormatting.GREEN)
                .append(Component.literal("Deploy " + selectedTitan(stack).getDisplayName()).withStyle(ChatFormatting.WHITE)));
        if (this.fixedClass == null) {
            tooltip.add(Component.literal("Shift + Right-Click in air: ").withStyle(ChatFormatting.DARK_AQUA)
                    .append(Component.literal("Switch Frame Type (6 Variants)").withStyle(ChatFormatting.YELLOW)));
        }
    }
}
