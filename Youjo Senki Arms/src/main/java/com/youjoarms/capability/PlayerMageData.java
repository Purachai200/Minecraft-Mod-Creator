package com.youjoarms.capability;

import com.youjoarms.config.YoujoArmsConfig;
import com.youjoarms.formula.FormulaType;
import net.minecraft.nbt.CompoundTag;

public class PlayerMageData {
    private int mana;
    private int maxMana = 100;
    private FormulaType selectedFormula = FormulaType.NONE;
    private boolean charging = false;
    private int chargeTicks = 0;
    private int shieldTicks = 0;

    public PlayerMageData() {
        this.mana = 100;
    }

    public int getMana() {
        return mana;
    }

    public void setMana(int mana) {
        this.mana = Math.max(0, Math.min(mana, getMaxMana()));
    }

    public int getMaxMana() {
        if (YoujoArmsConfig.COMMON_SPEC.isLoaded()) {
            return YoujoArmsConfig.COMMON.maxMana.get();
        }
        return maxMana;
    }

    public boolean consumeMana(int amount) {
        if (this.mana >= amount) {
            this.mana -= amount;
            return true;
        }
        return false;
    }

    public void regen(int amount) {
        setMana(this.mana + amount);
    }

    public FormulaType getSelectedFormula() {
        return selectedFormula;
    }

    public void setSelectedFormula(FormulaType formula) {
        this.selectedFormula = formula != null ? formula : FormulaType.NONE;
    }

    public boolean isCharging() {
        return charging;
    }

    public void setCharging(boolean charging) {
        this.charging = charging;
        if (!charging) {
            this.chargeTicks = 0;
        }
    }

    public int getChargeTicks() {
        return chargeTicks;
    }

    public void setChargeTicks(int ticks) {
        this.chargeTicks = ticks;
    }

    public void tickCharge() {
        if (charging) {
            this.chargeTicks++;
        }
    }

    public int getShieldTicks() {
        return shieldTicks;
    }

    public void setShieldTicks(int ticks) {
        this.shieldTicks = Math.max(0, ticks);
    }

    public boolean isFullyCharged() {
        if (selectedFormula == FormulaType.NONE) return false;
        return charging && chargeTicks >= selectedFormula.getChargeTicks();
    }

    public float getChargeProgress() {
        if (selectedFormula == FormulaType.NONE || !charging) return 0f;
        int required = selectedFormula.getChargeTicks();
        if (required <= 0) return 1f;
        return Math.min(1.0f, (float) chargeTicks / required);
    }

    public CompoundTag serializeNBT() {
        CompoundTag tag = new CompoundTag();
        tag.putInt("Mana", mana);
        tag.putInt("Formula", selectedFormula.getId());
        tag.putBoolean("Charging", charging);
        tag.putInt("ChargeTicks", chargeTicks);
        tag.putInt("ShieldTicks", shieldTicks);
        return tag;
    }

    public void deserializeNBT(CompoundTag tag) {
        this.mana = tag.getInt("Mana");
        this.selectedFormula = FormulaType.byId(tag.getInt("Formula"));
        this.charging = tag.getBoolean("Charging");
        this.chargeTicks = tag.getInt("ChargeTicks");
        this.shieldTicks = tag.getInt("ShieldTicks");
    }

    public void copyFrom(PlayerMageData source) {
        this.mana = source.mana;
        this.selectedFormula = source.selectedFormula;
        this.charging = source.charging;
        this.chargeTicks = source.chargeTicks;
        this.shieldTicks = source.shieldTicks;
    }
}
