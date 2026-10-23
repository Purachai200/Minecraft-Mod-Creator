# Titan Combat v1.1.1 (Hotfix) - Release Notes สำหรับอัปโหลด CurseForge

### 📌 File Name:
`titancombat-1.1.1.jar`

### 🎮 Compatible Game Version:
- **Minecraft**: `1.20.1`
- **ModLoader**: `Forge` (47.1.0+)
- **Dependency**: `GeckoLib` (4.4.4+)

---

## 🇹🇭 บันทึกการอัปเดต (ภาษาไทย)

### ⚡ การแก้ไขด่วนในเวอร์ชัน 1.1.1 (Hotfix):
- **แก้ปัญหาเกม Crash จาก GeckoLib**: แก้ไขข้อผิดพลาด `JsonSyntaxException: Not a JSON Object` ตอนโหลดเกม โดยการคลีนแท็กอนุภาคตกค้างจาก Bedrock Animation ออกจากหุ่นยนต์ทั้ง 7 ตัว ทำให้ตัวเกมเปิดได้ลื่นไหล แอนิเมชันเล่นได้ครบทุกท่วงท่า 100%

### ✨ ไฮไลต์หลักของระบบ Titan Combat:
1. **พอร์ตโมเดลและแอนิเมชันหุ่นรบครบทั้ง 7 คลาส**:
   - **Ion**: ปืนลำแสงอนุภาคความแม่นยำสูง
   - **Scorch**: เครื่องยิงลูกระเบิดเพลิงเทอร์ไมต์ เผาทำลายพื้นที่
   - **Ronin**: ปืนลูกซอง Leadwall รัศมีม่านกระสุนกว้าง
   - **Tone**: ปืนใหญ่ Tracker Cannon 40 มม. วิถีทำลายล้าง
   - **Legion**: ปืนกลหมุน 6 ลำกล้อง Predator Minigun อัตราการยิงมหาศาล
   - **Monarch**: ปืนกลหนัก XO-16 พร้อมระบบดูดเกราะอัตโนมัติ
   - **Northstar**: สไนเปอร์เรลกันพลาสมาพลังงานสูง นัดเดียวจอด
2. **ระบบ AI หลบหลีกสิ่งกีดขวางอัจฉริยะ (Terrain Hazard Pathfinding)**:
   - **กันตกบ่อลาวา**: หุ่นสแกนทิศทางเดินล่วงหน้าและหลีกเลี่ยงลาวาอัตโนมัติ
   - **กันตกเหวและหน้าผา**: ตรวจจับความลึกของหน้าผาตัดชัน ไม่ก้าวตกเหวเด็ดขาด พร้อมระบบ Brake Assist ป้องกันนักบินพลัดตกขณะขับขี่
   - **บดขยี้พืชพรรณธรรมชาติ (Foliage Trample)**: เหยียบทำลายใบไม้ป่าและพุ่มไม้ธรรมชาติรอบตัว โดยไม่ทำลายสิ่งก่อสร้างหรือใบไม้ตกแต่งของผู้เล่น
   - **ระบบแจ้งเตือนติดสิ่งกีดขวาง (Anti-Stuck Watchdog)**: แจ้งเตือนพิกัดทางวิทยุหากหุ่นติดซอกหินเกิน 3 วินาที
3. **ระบบสลับแบตเตอรี่และแท่นชาร์จ (Swappable Battery & Charger Station)**:
   - นำ Titan Core Battery ไปชาร์จหุ่น จะได้ Depleted Battery คืนมาในตัว
   - แท่นชาร์จแบตเตอรี่ (`battery_charger`) รองรับพลังงาน Forge Energy (FE) จากสายไฟม็อดเทค และรองรับการใส่ถ่าน/หินแดง/ถังลาวาแบบ Vanilla ได้โดยตรง
4. **ความปลอดภัยและลวดลายพราง**:
   - ระบบสิทธิ์นักบินไบโอเมตริก ป้องกันคนอื่นมาขโมยหุ่นในเซิร์ฟเวอร์
   - แท่นจอดโรงเก็บ (`hangar_dock`) ซ่อมบำรุงและจอดโชว์
   - ลายพราง 8 รูปแบบ ย้อมสีได้ด้วยสีย้อมทั่วไป

---

## 🇬🇧 Changelog (English)

### v1.1.1 Hotfix:
- Fixed a startup crash caused by Bedrock particle array syntax in GeckoLib 4 animation files.
- All 7 Titan animations now deserialize and play smoothly without errors.

### Features & Improvements:
- **7 Titan Classes Ported**: Ion, Scorch, Ronin, Tone, Legion, Monarch, and Northstar with authentic animations and weapon systems.
- **Intelligent Hazard Pathfinding**: Autonomous cliff edge detection, lava avoidance, and natural foliage trample (protects player base persistent leaves).
- **Swappable Battery Infrastructure**: Depleted battery cycle + FE-compatible Battery Charging Station with standalone fuel support.
- **Biometric Security & Customization**: Anti-theft pilot licensing, Hangar Docking Pads, and 8 customizable dye camouflage patterns.
