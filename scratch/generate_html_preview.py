import json

with open(r'Titan Combat/src/main/resources/assets/titancombat/geo/exo_frame_titan.geo.json', 'r', encoding='utf-8') as f:
    geo = json.load(f)

cubes = []
for b in geo['minecraft:geometry'][0]['bones']:
    bname = b['name']
    if bname.startswith('armor_'):
        continue
    for c in b.get('cubes', []):
        o = c['origin']
        s = c['size']
        cubes.append({"bone": bname, "origin": o, "size": s})

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Knightmare Frame (RPI-13 Sutherland) 3D Preview</title>
<style>
  body {{ margin: 0; background: #121418; color: #fff; font-family: sans-serif; overflow: hidden; }}
  #info {{ position: absolute; top: 15px; left: 20px; z-index: 10; pointer-events: none; }}
  h2 {{ margin: 0 0 5px 0; color: #d49f38; letter-spacing: 1px; }}
  p {{ margin: 0; color: #9aa; font-size: 13px; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div id="info">
  <h2>RPI-13 SUTHERLAND (Knightmare Frame)</h2>
  <p>Authentic Code Geass Frame: Factsphere Head Optic, Chest Slash Harkens, Dorsal Ejection Pod, Ankle Landspinners</p>
  <p>Drag mouse to rotate, scroll to zoom</p>
</div>
<script>
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x13151b);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
camera.position.set(-50, 50, 70);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 42, 0);
controls.update();

// Lights
const amb = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(amb);
const dir = new THREE.DirectionalLight(0xffeedd, 0.85);
dir.position.set(40, 80, 50);
scene.add(dir);
const backLight = new THREE.DirectionalLight(0x4466aa, 0.4);
backLight.position.set(-40, 20, -50);
scene.add(backLight);

// Grid
const grid = new THREE.GridHelper(100, 20, 0xd49f38, 0x2a3040);
scene.add(grid);

const cubesData = {json.dumps(cubes)};

const MAT_BASE = new THREE.MeshStandardMaterial({{ color: 0x5a566a, roughness: 0.4, metalness: 0.3 }});
const MAT_DARK = new THREE.MeshStandardMaterial({{ color: 0x25252c, roughness: 0.6, metalness: 0.5 }});
const MAT_GOLD = new THREE.MeshStandardMaterial({{ color: 0xd49f38, roughness: 0.3, metalness: 0.6 }});
const MAT_RED = new THREE.MeshBasicMaterial({{ color: 0xff1e38 }});
const MAT_VENT = new THREE.MeshStandardMaterial({{ color: 0x16181e, roughness: 0.8 }});

cubesData.forEach(c => {{
  const [dx, dy, dz] = c.size;
  const [x, y, z] = c.origin;
  const geom = new THREE.BoxGeometry(dx, dy, dz);
  let mat = MAT_BASE;
  const b = c.bone;
  if (b === 'head' && z < -4.8) mat = MAT_RED;
  else if (b === 'head' && dy >= 4.5 && dx <= 1.0) mat = MAT_GOLD;
  else if (b === 'body3' && z < -5.5 && dx <= 2.6) mat = MAT_GOLD;
  else if (b === 'body3' && z > 4.0) mat = y <= 64 ? MAT_VENT : MAT_DARK;
  else if (b === 'body2') mat = MAT_DARK;
  else if (b.includes('Hand')) mat = MAT_DARK;
  else if (b.includes('Leg') && x < -11 && dx <= 1.0) mat = MAT_GOLD;
  else if (b.includes('Leg') && x < -11 && dy >= 5) mat = MAT_DARK;

  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.set(x + dx/2, y + dy/2, z + dz/2);
  scene.add(mesh);
}});

function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
animate();

window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});
</script>
</body>
</html>
"""

with open(r"C:\Users\Purachai\.gemini\antigravity\brain\dc63a5aa-ae1e-416f-8afe-779a698ca425\exo_model_preview.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Updated HTML 3D preview successfully.")
