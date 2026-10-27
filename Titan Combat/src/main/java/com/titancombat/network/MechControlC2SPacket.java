package com.titancombat.network;

import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class MechControlC2SPacket {
    private final float forward;
    private final float strafe;
    private final boolean dashing;
    private final boolean firing;
    private final boolean defense;
    private final boolean core;
    private final boolean melee;
    private final boolean kneel;

    public MechControlC2SPacket(float forward, float strafe, boolean dashing, boolean firing) {
        this(forward, strafe, dashing, firing, false, false, false, false);
    }

    public MechControlC2SPacket(float forward, float strafe, boolean dashing, boolean firing, boolean defense, boolean core) {
        this(forward, strafe, dashing, firing, defense, core, false, false);
    }

    public MechControlC2SPacket(float forward, float strafe, boolean dashing, boolean firing, boolean defense, boolean core, boolean melee) {
        this(forward, strafe, dashing, firing, defense, core, melee, false);
    }

    public MechControlC2SPacket(float forward, float strafe, boolean dashing, boolean firing, boolean defense, boolean core, boolean melee, boolean kneel) {
        this.forward = forward;
        this.strafe = strafe;
        this.dashing = dashing;
        this.firing = firing;
        this.defense = defense;
        this.core = core;
        this.melee = melee;
        this.kneel = kneel;
    }

    public MechControlC2SPacket(FriendlyByteBuf buf) {
        this.forward = buf.readFloat();
        this.strafe = buf.readFloat();
        this.dashing = buf.readBoolean();
        this.firing = buf.readBoolean();
        this.defense = buf.readBoolean();
        this.core = buf.readBoolean();
        this.melee = buf.readBoolean();
        this.kneel = buf.readBoolean();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeFloat(this.forward);
        buf.writeFloat(this.strafe);
        buf.writeBoolean(this.dashing);
        buf.writeBoolean(this.firing);
        buf.writeBoolean(this.defense);
        buf.writeBoolean(this.core);
        buf.writeBoolean(this.melee);
        buf.writeBoolean(this.kneel);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null) {
                if (player.getVehicle() instanceof BaseMechEntity mech) {
                    if (this.dashing) {
                        mech.performDash(this.forward, this.strafe);
                    }
                    if (this.defense) {
                        mech.toggleDefenseMatrix(player);
                    }
                    if (this.core) {
                        mech.activateCoreOverdrive(player);
                    }
                    if (this.firing && mech instanceof BaseTitanEntity titan) {
                        titan.firePrimaryWeapon(player);
                    }
                    if (this.melee && mech instanceof BaseTitanEntity titan) {
                        titan.performMeleeAttack(player);
                    }
                    if (this.kneel && mech instanceof BaseTitanEntity titan) {
                        titan.toggleKneel();
                    }
                } else if (player.getVehicle() instanceof com.titancombat.entity.transport.TitanSkyCraneDroneEntity drone) {
                    if (this.firing) {
                        drone.performAirborneHotDrop(player);
                    }
                }
            }
        });
        return true;
    }
}
