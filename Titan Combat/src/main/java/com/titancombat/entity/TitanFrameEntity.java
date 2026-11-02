package com.titancombat.entity;

import com.titancombat.item.TitanArmorItem;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

public abstract class TitanFrameEntity extends BaseTitanEntity {
    public static final EntityDataAccessor<Boolean> DATA_ARMOR_HEAD =
            SynchedEntityData.defineId(TitanFrameEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_ARMOR_CHEST =
            SynchedEntityData.defineId(TitanFrameEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_ARMOR_ARMS =
            SynchedEntityData.defineId(TitanFrameEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_ARMOR_LEGS =
            SynchedEntityData.defineId(TitanFrameEntity.class, EntityDataSerializers.BOOLEAN);

    public static final EntityDataAccessor<Integer> DATA_THEME_HEAD =
            SynchedEntityData.defineId(TitanFrameEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_THEME_CHEST =
            SynchedEntityData.defineId(TitanFrameEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_THEME_ARMS =
            SynchedEntityData.defineId(TitanFrameEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_THEME_LEGS =
            SynchedEntityData.defineId(TitanFrameEntity.class, EntityDataSerializers.INT);

    public TitanFrameEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_ARMOR_HEAD, false);
        this.entityData.define(DATA_ARMOR_CHEST, false);
        this.entityData.define(DATA_ARMOR_ARMS, false);
        this.entityData.define(DATA_ARMOR_LEGS, false);

        this.entityData.define(DATA_THEME_HEAD, TitanArmorTheme.VANGUARD.getId());
        this.entityData.define(DATA_THEME_CHEST, TitanArmorTheme.VANGUARD.getId());
        this.entityData.define(DATA_THEME_ARMS, TitanArmorTheme.VANGUARD.getId());
        this.entityData.define(DATA_THEME_LEGS, TitanArmorTheme.VANGUARD.getId());
    }

    public boolean hasHeadArmor() {
        return this.entityData.get(DATA_ARMOR_HEAD);
    }

    public void setHeadArmor(boolean equipped) {
        this.entityData.set(DATA_ARMOR_HEAD, equipped);
    }

    public boolean hasChestArmor() {
        return this.entityData.get(DATA_ARMOR_CHEST);
    }

    public void setChestArmor(boolean equipped) {
        this.entityData.set(DATA_ARMOR_CHEST, equipped);
    }

    public boolean hasArmsArmor() {
        return this.entityData.get(DATA_ARMOR_ARMS);
    }

    public void setArmsArmor(boolean equipped) {
        this.entityData.set(DATA_ARMOR_ARMS, equipped);
    }

    public boolean hasLegsArmor() {
        return this.entityData.get(DATA_ARMOR_LEGS);
    }

    public void setLegsArmor(boolean equipped) {
        this.entityData.set(DATA_ARMOR_LEGS, equipped);
    }

    public TitanArmorTheme getHeadTheme() {
        return TitanArmorTheme.byId(this.entityData.get(DATA_THEME_HEAD));
    }

    public void setHeadTheme(TitanArmorTheme theme) {
        this.entityData.set(DATA_THEME_HEAD, theme.getId());
    }

    public TitanArmorTheme getChestTheme() {
        return TitanArmorTheme.byId(this.entityData.get(DATA_THEME_CHEST));
    }

    public void setChestTheme(TitanArmorTheme theme) {
        this.entityData.set(DATA_THEME_CHEST, theme.getId());
    }

    public TitanArmorTheme getArmsTheme() {
        return TitanArmorTheme.byId(this.entityData.get(DATA_THEME_ARMS));
    }

    public void setArmsTheme(TitanArmorTheme theme) {
        this.entityData.set(DATA_THEME_ARMS, theme.getId());
    }

    public TitanArmorTheme getLegsTheme() {
        return TitanArmorTheme.byId(this.entityData.get(DATA_THEME_LEGS));
    }

    public void setLegsTheme(TitanArmorTheme theme) {
        this.entityData.set(DATA_THEME_LEGS, theme.getId());
    }

    @Override
    public void openCustomInventoryScreen(Player player) {
        syncInventoryFromArmor();
        super.openCustomInventoryScreen(player);
    }

    public void syncArmorFromInventory() {
        ItemStack head = this.titanInventory.getItem(com.titancombat.gui.TitanMenu.ARMOR_HEAD_SLOT);
        if (!head.isEmpty() && head.getItem() instanceof TitanArmorItem) {
            setHeadArmor(true);
            setHeadTheme(TitanArmorItem.getTheme(head));
        } else {
            setHeadArmor(false);
        }

        ItemStack chest = this.titanInventory.getItem(com.titancombat.gui.TitanMenu.ARMOR_CHEST_SLOT);
        if (!chest.isEmpty() && chest.getItem() instanceof TitanArmorItem) {
            setChestArmor(true);
            setChestTheme(TitanArmorItem.getTheme(chest));
        } else {
            setChestArmor(false);
        }

        ItemStack arms = this.titanInventory.getItem(com.titancombat.gui.TitanMenu.ARMOR_ARMS_SLOT);
        if (!arms.isEmpty() && arms.getItem() instanceof TitanArmorItem) {
            setArmsArmor(true);
            setArmsTheme(TitanArmorItem.getTheme(arms));
        } else {
            setArmsArmor(false);
        }

        ItemStack legs = this.titanInventory.getItem(com.titancombat.gui.TitanMenu.ARMOR_LEGS_SLOT);
        if (!legs.isEmpty() && legs.getItem() instanceof TitanArmorItem) {
            setLegsArmor(true);
            setLegsTheme(TitanArmorItem.getTheme(legs));
        } else {
            setLegsArmor(false);
        }
    }

    public void syncInventoryFromArmor() {
        if (hasHeadArmor() && this.titanInventory.getItem(com.titancombat.gui.TitanMenu.ARMOR_HEAD_SLOT).isEmpty()) {
            ItemStack st = new ItemStack(com.titancombat.item.ModItems.TITAN_ARMOR_HEAD.get());
            TitanArmorItem.setTheme(st, getHeadTheme());
            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_HEAD_SLOT, st);
        }
        if (hasChestArmor() && this.titanInventory.getItem(com.titancombat.gui.TitanMenu.ARMOR_CHEST_SLOT).isEmpty()) {
            ItemStack st = new ItemStack(com.titancombat.item.ModItems.TITAN_ARMOR_CHEST.get());
            TitanArmorItem.setTheme(st, getChestTheme());
            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_CHEST_SLOT, st);
        }
        if (hasArmsArmor() && this.titanInventory.getItem(com.titancombat.gui.TitanMenu.ARMOR_ARMS_SLOT).isEmpty()) {
            ItemStack st = new ItemStack(com.titancombat.item.ModItems.TITAN_ARMOR_ARMS.get());
            TitanArmorItem.setTheme(st, getArmsTheme());
            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_ARMS_SLOT, st);
        }
        if (hasLegsArmor() && this.titanInventory.getItem(com.titancombat.gui.TitanMenu.ARMOR_LEGS_SLOT).isEmpty()) {
            ItemStack st = new ItemStack(com.titancombat.item.ModItems.TITAN_ARMOR_LEGS.get());
            TitanArmorItem.setTheme(st, getLegsTheme());
            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_LEGS_SLOT, st);
        }
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);

        // Open Frame Customization & Maintenance Screen with Sneak + Right-Click with empty hand
        if (player.isShiftKeyDown() && held.isEmpty()) {
            if (!this.level().isClientSide) {
                openCustomInventoryScreen(player);
                this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_DOOR_OPEN, SoundSource.PLAYERS, 1.0F, 1.0F);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // Modular Armor Installation & Swapping via right-click with TitanArmorItem
        if (held.getItem() instanceof TitanArmorItem armorItem) {
            if (!this.level().isClientSide) {
                TitanArmorTheme newTheme = TitanArmorItem.getTheme(held);
                boolean installed = false;
                boolean swapped = false;
                TitanArmorTheme oldTheme = null;

                switch (armorItem.getArmorSlot()) {
                    case HEAD -> {
                        if (!hasHeadArmor()) {
                            setHeadArmor(true);
                            setHeadTheme(newTheme);
                            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_HEAD_SLOT, held.copyWithCount(1));
                            installed = true;
                        } else if (getHeadTheme() != newTheme) {
                            oldTheme = getHeadTheme();
                            setHeadTheme(newTheme);
                            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_HEAD_SLOT, held.copyWithCount(1));
                            swapped = true;
                        }
                    }
                    case CHEST -> {
                        if (!hasChestArmor()) {
                            setChestArmor(true);
                            setChestTheme(newTheme);
                            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_CHEST_SLOT, held.copyWithCount(1));
                            installed = true;
                        } else if (getChestTheme() != newTheme) {
                            oldTheme = getChestTheme();
                            setChestTheme(newTheme);
                            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_CHEST_SLOT, held.copyWithCount(1));
                            swapped = true;
                        }
                    }
                    case ARMS -> {
                        if (!hasArmsArmor()) {
                            setArmsArmor(true);
                            setArmsTheme(newTheme);
                            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_ARMS_SLOT, held.copyWithCount(1));
                            installed = true;
                        } else if (getArmsTheme() != newTheme) {
                            oldTheme = getArmsTheme();
                            setArmsTheme(newTheme);
                            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_ARMS_SLOT, held.copyWithCount(1));
                            swapped = true;
                        }
                    }
                    case LEGS -> {
                        if (!hasLegsArmor()) {
                            setLegsArmor(true);
                            setLegsTheme(newTheme);
                            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_LEGS_SLOT, held.copyWithCount(1));
                            installed = true;
                        } else if (getLegsTheme() != newTheme) {
                            oldTheme = getLegsTheme();
                            setLegsTheme(newTheme);
                            this.titanInventory.setItem(com.titancombat.gui.TitanMenu.ARMOR_LEGS_SLOT, held.copyWithCount(1));
                            swapped = true;
                        }
                    }
                }

                if (installed || swapped) {
                    if (!player.getAbilities().instabuild) {
                        held.shrink(1);
                        if (swapped && oldTheme != null) {
                            ItemStack returnStack = new ItemStack(armorItem);
                            TitanArmorItem.setTheme(returnStack, oldTheme);
                            if (!player.getInventory().add(returnStack)) {
                                player.drop(returnStack, false);
                            }
                        }
                    }
                    this.level().playSound(null, this.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE, SoundSource.PLAYERS, 1.5F, 1.0F);
                    if (swapped) {
                        player.sendSystemMessage(Component.translatable("message.titancombat.armor_swapped_themed",
                                armorItem.getArmorSlot().getId(), newTheme.getDisplayName()));
                    } else {
                        player.sendSystemMessage(Component.translatable("message.titancombat.armor_installed_themed",
                                armorItem.getArmorSlot().getId(), newTheme.getDisplayName()));
                    }
                    return InteractionResult.sidedSuccess(this.level().isClientSide);
                } else {
                    player.sendSystemMessage(Component.translatable("message.titancombat.armor_already_installed", armorItem.getArmorSlot().getId()));
                }
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        return super.mobInteract(player, hand);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("ArmorHead", hasHeadArmor());
        tag.putBoolean("ArmorChest", hasChestArmor());
        tag.putBoolean("ArmorArms", hasArmsArmor());
        tag.putBoolean("ArmorLegs", hasLegsArmor());

        tag.putInt("ThemeHead", getHeadTheme().getId());
        tag.putInt("ThemeChest", getChestTheme().getId());
        tag.putInt("ThemeArms", getArmsTheme().getId());
        tag.putInt("ThemeLegs", getLegsTheme().getId());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("ArmorHead")) setHeadArmor(tag.getBoolean("ArmorHead"));
        if (tag.contains("ArmorChest")) setChestArmor(tag.getBoolean("ArmorChest"));
        if (tag.contains("ArmorArms")) setArmsArmor(tag.getBoolean("ArmorArms"));
        if (tag.contains("ArmorLegs")) setLegsArmor(tag.getBoolean("ArmorLegs"));

        if (tag.contains("ThemeHead")) setHeadTheme(TitanArmorTheme.byId(tag.getInt("ThemeHead")));
        if (tag.contains("ThemeChest")) setChestTheme(TitanArmorTheme.byId(tag.getInt("ThemeChest")));
        if (tag.contains("ThemeArms")) setArmsTheme(TitanArmorTheme.byId(tag.getInt("ThemeArms")));
        if (tag.contains("ThemeLegs")) setLegsTheme(TitanArmorTheme.byId(tag.getInt("ThemeLegs")));

        syncInventoryFromArmor();
    }
}
