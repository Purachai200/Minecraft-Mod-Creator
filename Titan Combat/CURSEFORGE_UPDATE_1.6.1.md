# Titan Combat v1.6.1 (Pilot Immersion Overhaul) - Release Notes สำหรับอัปโหลด CurseForge

### 📌 File Name:
`titancombat-1.6.1.jar`

### 🎮 Compatible Game Version:
- **Minecraft**: `1.20.1`
- **ModLoader**: `Forge` (47.1.0+)
- **Dependency**: `GeckoLib` (4.4.4+)

### 🖼️ Screenshots (โฟลเดอร์ `promo/`)
`01_lineup` · `02_ion_hero` · `03_legion_barrier` · `04_northstar_jump` · `05_scorch_parked` · `07_cockpit` · `09_bay` · `10_eject`

---

## 🇹🇭 บันทึกการอัปเดต (ภาษาไทย)

### 🛩️ ขับหุ่นแบบสมจริง
- **ห้องนักบิน 3D มุมมองบุคคลที่ 1**: เห็นโครงกระจกห้องนักบิน แผงหน้าปัด และแขนกับปืนของหุ่นจริง ๆ ขยับตามการยิง การต่อย การเดิน
- **HUD ใหม่สไตล์ Titanfall**: ฉากบูตระบบตอนขึ้นหุ่น, เข็มทิศ, เรดาร์, แถบเกราะ/โล่, ช่องแดช, เกจ Core, เป้าเล็งตามชนิดปืน, เตือนเกราะวิกฤต
- **ขึ้นหุ่นแบบมีลำดับ**: หุ่นที่เรียกมาจะคุกเข่ารอพร้อมเปิดฝาห้องนักบิน ขึ้นแล้วฝาปิดและหุ่นลุกยืนเอง
- **หน้าเก็บของหุ่น (E) ออกแบบใหม่**: ภาพหุ่น 3D แบบสด, แถบสถานะ, ช่องแบตเตอรี่/กระสุน/อาวุธ/สัมภาระ

### 🔫 ระบบอาวุธใหม่
- **ปืน 7 แบบ ใส่หุ่นตัวไหนก็ได้**: Splitter Rifle, Thermite Launcher, Leadwall, 40mm Tracker, Predator Cannon, XO-16, Plasma Railgun
- **หุ่นเริ่มต้นมือเปล่า** ต้องใส่โมดูลอาวุธในช่อง WEAPON ก่อน
- **แม็กกาซีน + กระสุนเฉพาะปืน**: รีโหลด [R] ยกปืนก่อนยิง (มินิกันต้องหมุนลำกล้องก่อน) ลดปืน [H]
- **เกราะกันกระสุน**: กระสุนปืนเล็กจากม็อดปืน (TACZ, Superb Warfare) แทบไม่เข้า ระเบิดและอาวุธหุ่นยังทำดาเมจได้ นักบินในห้องปลอดภัย
- **Defense Matrix** มีโดมพลังงานสีฟ้าล้อมรอบหุ่น

### 🦿 การเคลื่อนไหว
- เสียงเท้าตรงจังหวะเท้าแตะพื้นจริง พร้อมฝุ่นและแรงสั่น
- ความเร็วตรงกับระยะก้าว เท้าไม่ไถล ไม่จมพื้นตอนเดิน มีน้ำหนักตอนออกตัว/หยุด, วิ่ง (Sprint)
- แดช 3 ครั้ง + กระโดดไอพ่น (Space) พร้อมเอฟเฟกต์ไอพ่น
- ลำตัวหันตามจุดเล็ง ขาหมุนตาม ตัวเอนตามการเร่ง/เลี้ยว
- ขึ้นลงบล็อกนุ่มนวล ยืนบนพื้นต่างระดับเท้าวางพอดี
- ต่อยมีจังหวะง้าง ดาเมจเข้าตอนหมัดถึง, Ronin ฟันดาบคอมโบ

### 🚀 ดีดตัวออก (Eject)
- กด [X] สองครั้ง (หรือครั้งเดียวตอนหุ่นใกล้พัง): ฝาห้องนักบินระเบิดออก นักบินพุ่งขึ้นฟ้าพร้อมไอพ่น ร่อนลงช้า ๆ อย่างปลอดภัย หุ่นทำลายตัวเองหลังจากนั้น 2.5 วินาที

### 🎨 ไอเทมใหม่ทั้งหมด
- วาดไอเทมใหม่ทั้งหมดเป็นพิกเซลอาร์ต 32x32 + โมดูลอาวุธ 7 ชิ้น + กระสุน 7 ชนิด

### 🛠️ แก้บัค
- เป้าเล็งตรงกับจุดที่กระสุนตก ทั้งมุมมองบุคคลที่ 1 และ 3, กด Ctrl (วิ่ง) แล้วแขน/ปืนในห้องนักบินไม่หมุนมั่วอีก, หุ่นมือเปล่าไม่ทำท่าถือปืน
- แขนไขว้/ผิดตำแหน่งตอนคุกเข่า, หุ่นค้างไม่มีอนิเมชันหลังจอดแล้วขึ้นใหม่, ปืนซ้อนสองกระบอก, กระสุนตกไม่ตรงเป้า, ตำแหน่งนักบินลอยนอกห้องนักบิน, กด Z ค้างแล้วรัว

---

## 🇬🇧 Changelog (English)

### Cockpit & HUD
- Real first-person cockpit: canopy frame, instrument panel and the titan's own arms/weapon rendered around the camera, animated for firing, melee and walking.
- New Titanfall-style HUD: boot sequence on embark, compass, radar, hull/shield bars, dash cells, core meter, per-weapon reticles, critical alerts.
- Boarding sequence: summoned titans kneel with the hatch open; boarding seals the hatch and the titan stands up.
- Redesigned Cockpit Bay (E) with a live 3D titan preview and weapon/munitions/reactor/cargo slots.

### Weapons
- 7 weapon modules that fit any chassis. Titans start unarmed.
- Per-weapon magazines and ammo, reload [R], raise-before-fire (Predator spin-up), lower weapon [H].
- Hull plating vs. infantry guns (TACZ / Superb Warfare): small arms mostly ricochet; explosives and titan weapons hurt. The pilot is protected inside.
- Defense Matrix shows a blue energy dome.

### Movement
- Footsteps synced to the animation's foot plants, with dust and screen shake.
- Stride-matched ground speed (no foot sliding or sinking), inertia, sprint.
- 3 dash charges + jump jets with thruster effects.
- Torso follows aim, legs turn after it, lean into acceleration and turns.
- Smooth step-up/down and foot placement on uneven ground.
- Melee with wind-up and impact timing; Ronin sword combos.

### Eject
- Press [X] twice (once when critically damaged): the hatch blows, the pilot rockets skyward and slow-falls to safety, and the titan self-destructs 2.5 s later.

### Items
- All items redrawn as 32x32 pixel art, plus 7 weapon modules and 7 magazine types.

### Fixes
- Shots land on the crosshair in first and third person; sprinting no longer spins the cockpit weapon rig; unarmed titans relax their arms.
- Crossed arms while kneeling, frozen animations after parking, duplicate guns, bullet drop missing the reticle, pilot floating outside the cockpit, Z key repeat.
