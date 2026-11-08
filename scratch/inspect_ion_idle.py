import json
with open('Titan Combat/src/main/resources/assets/titancombat/animations/ion_titan.animation.json', 'r') as f:
    anims = json.load(f)
idle = anims['animations']['animation.ion_titan.idle.arm']
import pprint
pprint.pprint(idle['bones'])
