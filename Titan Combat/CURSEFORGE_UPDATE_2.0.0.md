# Titan Combat v2.0.0: Strategic Transport & Frontline Deployment
## Release Notes สำหรับอัปโหลด CurseForge / Mod Update Changelog

### 📌 File Name:
`titancombat-2.0.0.jar`

### 🎮 Compatible Game Version:
- **Minecraft**: `1.20.1`
- **ModLoader**: `Forge` (47.1.0+ / Recommended 47.4.10)
- **Dependency**: `GeckoLib` (4.4.4+)

### 🖼️ Screenshots & Promo Materials (โฟลเดอร์ `promo/`):
- `autotest_transport_07_truck_cockpit_energy_hud.png` (Hauler Truck 1st-person cockpit with Energy PWR HUD)
- `autotest_transport_08_skycrane_flight_energy_hud.png` (SkyCrane Drone flight HUD with VSI & Energy bar)
- `autotest_transport_01_hauler_truck_mounted.png` (8x8 Heavy Hauler Truck with Titan loaded)
- `autotest_transport_03_skycrane_drone_airlift.png` (SkyCrane Drone airlifting Titan)
- `autotest_transport_04_cargo_barge_twin_titans.png` (Amphibious Cargo Barge with dual Titans)
- `autotest_transport_05_truck_driver_cab.png` (Hauler Truck 3D Driver Cockpit)
- `autotest_weapons_1st_01_cockpit_mining_drill.png` (Cockpit view with Heavy Mining Drill)
- `autotest_weapons_1st_02_cockpit_chainsaw.png` (Cockpit view with Hydraulic Chainsaw)
- `autotest_weapons_1st_03_cockpit_light_smg.png` (Cockpit view with Light Recon SMG)

---

## 🇹🇭 บันทึกการอัปเดตเวอร์ชัน 2.0.0 (ภาษาไทย)

การอัปเดตครั้งยิ่งใหญ่ **"Strategic Transport & Frontline Deployment"** พัฒนาระบบโลจิสติกส์การขนส่งไททันข้ามทวีป, ระบบเรียกหุ่นเข้าแนวหน้าด้วยคลื่นสัญญาณยุทธวิธี, แผงพลังงานเตาปฏิกรณ์และแท่นชาร์จแบตเตอรี่ FE, และการปรับปรุงโมเดลอาวุธในห้องนักบินมุมมองบุคคลที่ 1 อย่างสมบูรณ์แบบ!

### 🚚 1. กองยานพาหนะขนส่งไททันเชิงยุทธศาสตร์ (Strategic Transport Fleet)
- **8x8 Heavy Titan Hauler Truck**:
  - รถบรรทุกหุ้มเกราะ 8 ล้อขนาดมหึมา ออกแบบมาเพื่อลากจูงและขนส่งหุ่นยนต์ไททันข้ามสมรภูมิ
  - รองรับผู้โดยสาร 2 คน: คนขับ (Driver Cab) และผู้ช่วย (Passenger) พร้อมห้องโดยสาร 3D ภายใน
  - แท่นกระบะหลังพร้อมสลักล็อก (Winch Lock): นำหุ่นขึ้นท้ายรถแล้วคลิกขวาเพื่อล็อกตรึงหุ่นไว้แน่นหนา
  - มีสะพานทางลาดท้ายรถเปิด-ปิดได้ เพื่อความสะดวกในการเดินหุ่นขึ้น-ลง
- **SkyCrane Heavy Airlift Drone**:
  - โดรนยกหนัก 4 ใบพัดเจ็ต (Quad-Rotor VTOL) สำหรับลำเลียงไททันทางอากาศข้ามภูเขาและป่าลึก
  - ระบบ **Combat Hot-Drop**: สามารถปล่อยหุ่นไททันทิ้งลงมาจากระดับความสูงกลางอากาศสู่สมรภูมิแนวหน้าได้ทันที
  - มุมมองห้องนักบินโดรนแบบ Panoramic Canopy มองเห็นทัศนวิสัยกว้างไกล
- **Amphibious Titan Cargo Barge**:
  - เรือท้องแบนขนส่งสะเทินน้ำสะเทินบก สามารถขับเคลื่อนได้ทั้งในน้ำและบนบก
  - รองรับแท่นบรรทุกหุ่นไททันพร้อมกันได้ถึง **2 ตัว** (แท่นหน้าและแท่นหลัง) เหมาะสำหรับปฏิบัติการยกพลขึ้นบก

### 📡 2. ระบบเรียกและวาร์ปหุ่นสู่แนวหน้า (Tactical Warp & Frontline Recall)
- **กฎ 1 คนต่อ 1 ตัว (1:1 Pilot Binding Doctrine)**:
  - นักบิน 1 คนสามารถจับคู่กับหุ่นไททันคู่ใจได้เพียง 1 ตัวเท่านั้น เพื่อความสมดุลและไม่ให้เกิดความสับสนในการสั่งการ
  - มีระบบ Biometric Link ป้องกันผู้เล่นอื่นที่ไม่ได้รับอนุญาตมาขโมยสั่งการหรือขับหุ่นของคุณ
- **Pilot License / Data Knife**:
  - **คลิกขวาที่หุ่น**: ทำการจับคู่ (Biometric Sync) เพื่อลงทะเบียนเป็นนักบินประจำตัวหุ่น
  - **กด Sneak + คลิกขวา**: ล้างการจับคู่ (Unbind / Factory Reset) เพื่อปล่อยให้ผู้เล่นอื่นจับคู่ต่อ หรือย้ายไปผูกกับหุ่นตัวใหม่
- **ระยะเรียกแนวหน้า 250 บล็อก (Tactical Range Limit)**:
  - ใช้ **Titan Drop Beacon** หรือ **Hangar Transponder** เรียกหุ่นวาร์ปมายังตำแหน่งของคุณได้ในระยะ 250 บล็อก
  - สอดคล้องกับระบบโลจิสติกส์: ผู้เล่นต้องขนส่งหุ่นด้วยรถบรรทุก/เรือ/โดรนเข้ามาในพื้นที่ใกล้เคียงก่อน จึงจะสามารถเรียกวาร์ปบุกแนวหน้าได้!
- **ระบบปลดล็อกอัตโนมัติก่อนวาร์ป (Safe Auto-Dismount)**:
  - หากหุ่นกำลังถูกล็อกอยู่บนท้ายรถบรรทุก โดรน หรือเรือบาร์จ เมื่อถูกเรียกวาร์ประบบจะปลดล็อกและยกหุ่นลงจากยานพาหนะอัตโนมัติก่อนทำการวาร์ป ป้องกันปัญหายานพาหนะติดบัคหรือกระเด็นหาย

### ⚡ 3. เตาปฏิกรณ์และระบบพลังงานแบตเตอรี่ (Reactor Core & FE Energy Grid)
- **ระบบพลังงานยานพาหนะ (100,000 FE Vehicle Fuel Cell)**:
  - ยานพาหนะทุกคัน (Truck, Drone, Barge) ต้องใช้พลังงาน FE ในการขับเคลื่อน (ใช้ไฟขณะขับ/บิน/ล่องเรือ)
  - หากพลังงานหมด (0 FE) เครื่องยนต์จะดับ (Engine Stall) ไม่สามารถเร่งความเร็วหรือบินได้
  - เติมพลังงานได้ง่ายๆ เพียงถือแบตเตอรี่ Titan Battery คลิกขวาที่ตัวรถ เพื่อถ่ายโอนประจุไฟเข้ายานพาหนะทันที
- **ระดับแบตเตอรี่ใหม่ 3 ระดับ (Multi-Tier Power Cells)**:
  - **Tier 1 - Titan Core Battery (10,000 FE)**: แบตเตอรี่มาตรฐานพกพา
  - **Tier 2 - Heavy Titan Battery (50,000 FE)**: แบตเตอรี่รุ่นหนัก ชาร์จเตาปฏิกรณ์ของไททันเต็ม 100% ได้ในก้อนเดียว!
  - **Tier 3 - Superdense Fusion Battery (250,000 FE)**: แบตเตอรี่ฟิวชันความจุสูงพิเศษ เหมาะสำหรับกองยานพาหนะและการเดินทางไกลข้ามทวีป
  - ทุกระดับมีแถบแสดงประจุ 3 สีเรียลไทม์ (ฟ้า/เขียว, ส้ม, แดง)
- **Battery Charger Block (แท่นชาร์จแบตเตอรี่อุตสาหกรรม)**:
  - ขยายความจุแท่นชาร์จเป็น **500,000 FE** อัตราการชาร์จ 1,000 FE/t รองรับพลังงานมาตรฐาน Forge Energy (FE) จากทุกม็อด
  - ชาร์จแบตเตอรี่ได้ทุกระดับตั้งแต่ Tier 1 ถึง Tier 3
- **หน้าจอแสดงพลังงานยานพาหนะ (Transport Telemetry HUD)**:
  - แสดงผล **ความเร็ว (km/h & m/s)**, **ระดับความสูง (Altitude)**, **อัตราการไต่ระดับ (VSI m/s)**, **สถานะการล็อกหุ่น (Cargo Load)** และ **แถบพลังงานไฟฟ้า FE (PWR)** แบบเรียลไทม์ที่มุมจอด้านขวาล่าง

### 🛠️ 4. อัปเกรดโมเดลห้องนักบินมุมมองบุคคลที่ 1 (1st-Person Cockpit Model Overhaul)
- **Trooper Titan**:
  - **Heavy Mining Drill (หัวสว่านขุดเจาะ)**: แสดงหัวสว่านทรงกรวยและมอเตอร์ไฮดรอลิกสมจริงในห้องคนขับ
  - **Hydraulic Chainsaw (เลื่อยยนต์อุตสาหกรรม)**: แสดงใบเลื่อยยนต์ลายเหลือง-ดำพร้อมฟันเลื่อยในห้องคนขับ
  - ระบบตรวจจับอาวุธอัจฉริยะ: สลับโมเดลสว่าน/เลื่อยยนต์อัตโนมัติตามอาวุธที่ติดตั้ง และซ่อนเมื่อถืออาวุธปืนอื่น
- **Scout Titan**:
  - **Light Recon SMG**: แสดงโมเดลปืนกลเบาขนาดกะทัดรัดพร้อมศูนย์เล็งและกระบอกเก็บเสียงในห้องคนขับ
  - แสดงโมเดลปืนเหน็บหลัง (Stowed Back Bone) อย่างสวยงามเมื่อหุ่นจอดพักหรือยังไม่ได้ชักอาวุธ

### 📦 5. สูตรคราฟต์ครบวงจร (Complete Crafting Recipes)
- เพิ่มสูตรคราฟต์ในโต๊ะคราฟต์สำหรับยานพาหนะและอุปกรณ์ใหม่ครบถ้วน:
  - `titan_hauler_truck`
  - `titan_skycrane_drone`
  - `titan_cargo_barge`
  - `transport_winch`
  - `battery_charger`
  - `titan_battery`
- รองรับภาษาไทย (th_th) และภาษาอังกฤษ (en_us) ครบ 100%

---

## 🇬🇧 Changelog v2.0.0 (English)

The **"Strategic Transport & Frontline Deployment"** update introduces comprehensive Titan logistics, strategic multi-terrain transport vehicles, tactical front-line recall mechanics, an FE-powered reactor grid with portable batteries and charging stations, and a complete first-person cockpit model overhaul!

### 🚚 1. Strategic Titan Transport Fleet
- **8x8 Heavy Titan Hauler Truck**:
  - Heavy 8-wheel transport vehicle designed for cross-country Titan logistics.
  - 2-Player Seating: Fully modeled 3D driver's cab and co-pilot seat.
  - Rear Flatbed Titan Cradle with Winch Lock: Securely lock Titans onto the truck bed with right-click.
  - Deployable rear boarding ramp for easy loading/unloading.
- **SkyCrane Heavy Airlift Drone**:
  - Heavy quad-rotor VTOL transport aircraft capable of airlifting Titans over terrain barriers.
  - **Combat Hot-Drop Mechanism**: Drop Titans from altitude directly into frontline combat zones.
  - Panoramic cockpit view with tactical flight flight instrumentation.
- **Amphibious Titan Cargo Barge**:
  - Twin-cradle amphibious transport vessel operable on both land and water.
  - Dual-Titan capacity (Front & Rear loading cradles) for naval amphibious assault operations.

### 📡 2. Tactical Frontline Warp & Recall System
- **1:1 Pilot Binding Doctrine**:
  - Each pilot may bind to exactly one Titan at any given time, preventing tactical command conflicts.
  - Biometric Pilot Link ensures unauthorized players cannot hijack or issue commands to your Titan.
- **Pilot License / Data Knife Controls**:
  - **Right-Click Titan**: Establish Biometric Link (bind).
  - **Sneak + Right-Click**: Unbind / Factory Reset to release the Titan for other pilots.
- **250m Tactical Recall Range**:
  - **Titan Drop Beacon** and **Hangar Transponder** can warp your Titan directly to your frontline coordinates within a 250-block tactical radius.
  - Encourages vehicle logistics: Transport your Titans near the combat sector using trucks, drones, or barges before warping them into the hotspot!
- **Safe Auto-Dismount on Recall**:
  - If a Titan is secured onto a transport bed (Truck, Drone, or Barge), recalling it automatically detaches the winch and dismounts the Titan before warping, preventing vehicle glitching.

### ⚡ 3. Reactor Core & Forge Energy (FE) Grid
- **Vehicle Energy System (100,000 FE Fuel Cell)**:
  - Transport vehicles (Truck, Drone, Barge) consume FE while driving, flying, and cruising.
  - At 0 FE, the engine stalls and vehicle cannot accelerate. Refuel anytime by right-clicking the vehicle with any Titan Battery!
- **3 Battery Power Cell Tiers**:
  - **Tier 1 - Titan Core Battery (10,000 FE)**: Portable field battery.
  - **Tier 2 - Heavy Titan Battery (50,000 FE)**: Fills an entire Titan reactor to 100% in a single charge!
  - **Tier 3 - Superdense Fusion Battery (250,000 FE)**: Massive power supply for transport vehicles and fleet operations!
- **Battery Charger Block (500,000 FE Buffer)**:
  - Compatible with Forge Energy (FE) from all popular tech mods (Mekanism, Powah, Create, Thermal, etc.).
  - Charges all battery tiers (Tier 1-3) rapidly with active LED indicators.
- **Cockpit Energy & Flight Telemetry HUD**:
  - Real-time readout of Speed, Altitude, Climb Rate (VSI), Cargo Load Status, and Vehicle Energy PWR bar.

### 🛠️ 4. First-Person Cockpit Model Overhaul
- **Trooper Titan**:
  - Custom first-person cockpit geometry for the **Heavy Mining Drill** (drill cone & motor assembly).
  - Custom first-person cockpit geometry for the **Hydraulic Chainsaw** (hazard-striped guide bar & cutting chain).
  - Dynamic bone controller seamlessly toggles drill vs. chainsaw models based on equipped utility tools.
- **Scout Titan**:
  - Custom first-person cockpit geometry for the **Light Recon SMG** (receiver, iron sights, and suppressor).
  - Correct stowed weapon mesh on back holster when idling or docked.

### 📦 5. Complete Recipe & Localization Support
- Full crafting table recipes for all transport vehicles, transport winch, battery charger, and titan batteries.
- 100% localized in English (`en_us`) and Thai (`th_th`).
