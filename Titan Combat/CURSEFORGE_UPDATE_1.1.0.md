# Titan Combat v1.1.0 - Release Notes (ข้อความสำหรับอัปโหลด CurseForge)

### 📌 File Name:
`titancombat-1.1.0.jar`

### 🎮 Compatible Game Version:
- **Minecraft**: `1.20.1`
- **ModLoader**: `Forge` (47.1.0+)
- **Dependency**: `GeckoLib` (4.4.4+)

---

## 🇹🇭 บันทึกการอัปเดต (ภาษาไทย)

### ✨ ไฮไลต์หลักในเวอร์ชัน 1.1.0:
1. **พอร์ตโมเดลหุ่นรบระดับโปรครบทั้ง 7 คลาส**:
   - **Ion**: ปืนลำแสงอนุภาคพลังงานความแม่นยำสูง
   - **Scorch**: เครื่องยิงกระสุนเพลิงเทอร์ไมต์ สร้างดาเมจไฟเผาพื้นที่
   - **Ronin**: ปืนลูกซอง Leadwall ยิงม่านกระสุนกระจายระยะประชิด
   - **Tone**: ปืนใหญ่ Tracker Cannon 40 มม. วิถีตรงพลังทำลายล้าง
   - **Legion**: ปืนกลหมุน 6 ลำกล้อง Predator Minigun ยิงกดดันต่อเนื่อง
   - **Monarch**: ปืนกลหนัก XO-16 พร้อมระบบดูดกลืนพลังงานฟื้นฟูโอเวอร์ชิลด์
   - **Northstar**: สไนเปอร์เรลกันพลาสมาพลังงานสูง นัดเดียวสะเทือนสนามรบ
2. **ระบบ AI หลบหลีกสิ่งกีดขวางอัจฉริยะ (Terrain Hazard Pathfinding)**:
   - **กันตกบ่อลาวา**: หุ่นจะตรวจจับความร้อนและหลีกเลี่ยงไม่เดินลงลาวา
   - **กันตกเหวและหน้าผา**: ติดตั้งเซนเซอร์ตรวจจับความลึก หากเป็นหน้าผาตัดลึกเกิน 3 บล็อก หุ่นจะไม่ก้าวลงไปเด็ดขาด (มีระบบ Brake Assist ขณะขับขี่)
   - **บดขยี้พืชพรรณธรรมชาติ (Foliage Trample)**: เหยียบทำลายใบไม้ป่าและพุ่มไม้ธรรมชาติ โดยไม่ทำลายสิ่งก่อสร้างหรือใบไม้ที่ผู้เล่นนำมาตกแต่งบ้าน
   - **ระบบเตือนติดสิ่งกีดขวาง (Anti-Stuck Watchdog)**: แจ้งเตือนพิกัดทางวิทยุหากหุ่นติดซอกหินเกิน 3 วินาที
3. **ระบบสลับแบตเตอรี่และแท่นชาร์จ (Swappable Battery & Charger Station)**:
   - นำ Titan Core Battery ไปชาร์จหุ่น จะได้ Depleted Battery คืนมา
   - แท่นชาร์จแบตเตอรี่ (`battery_charger`) รองรับพลังงาน Forge Energy (FE) จากม็อดเทค และรองรับการใส่ถ่าน/หินแดง/ถังลาวาแบบ Vanilla ได้โดยตรง
4. **ความปลอดภัยและลวดลายพราง**:
   - ระบบสิทธิ์นักบินไบโอเมตริก ป้องกันคนอื่นมาขโมยหุ่นในเซิร์ฟเวอร์
   - แท่นจอดโรงเก็บ (`hangar_dock`) ซ่อมบำรุงและจอดโชว์
   - ลายพราง 8 รูปแบบ ย้อมสีได้ด้วยสีย้อมทั่วไป

---

## 🇬🇧 Changelog (English)

### Features & Improvements:
- **7 Titan Classes Ported**: Ion, Scorch, Ronin, Tone, Legion, Monarch, and Northstar with authentic animations and weapon systems.
- **Intelligent Hazard Pathfinding**: Autonomous cliff edge detection, lava avoidance, and natural foliage trample (protects player base persistent leaves).
- **Swappable Battery Infrastructure**: Depleted battery cycle + FE-compatible Battery Charging Station with standalone fuel support.
- **Biometric Security & Customization**: Anti-theft pilot licensing, Hangar Docking Pads, and 8 customizable dye camouflage patterns.
