package com.youjosenki.flight.client.model;

/**
 * Rig design catalogue. Geometry lives in assets/youjosenki/geo/<design>.geo.json (tools/model_spec.py)
 * and is rendered by client.geo.FlightRigRenderer through GeckoLib.
 */
public final class FlightUnitModel {
    private FlightUnitModel() {
    }

    public enum FlightDesign {
        MAGE_UNIT("Imperial Aerial Mage Rig"),
        BACK_JETPACK("Conventional Combat Jetpack"),
        TACTICAL_WINGS("Tactical Apex Glider-Jet"),
        HEAVY_ROCKET("Titan Industrial Rocket Rig"),
        TWIN_DRIVE_EXO("Type 95 Quad-Core Exoskeleton"),
        SIEGE_ARTILLERY("Titan Siege Assault Rig"),
        THRUST_BOOTS("Valkyrie Hover-Thrust Boots"),
        HYDRO_SKIMMER("Aquasurf Hydro-Glider Rig"),
        TACTICAL_SCUBA("Abyssal Combat Scuba Rig"),
        URBAN_EXO_LEGS("Urban Tactical Kinetic Exoskeleton"),
        DIVING_MASK("Abyssal Tactical Diving Mask");

        private final String displayName;

        FlightDesign(String name) {
            this.displayName = name;
        }

        public String getDisplayName() {
            return displayName;
        }
    }
}
