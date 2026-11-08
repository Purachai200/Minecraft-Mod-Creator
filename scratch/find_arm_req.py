import sys, json
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\Purachai\.gemini\antigravity\brain\dc63a5aa-ae1e-416f-8afe-779a698ca425\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'แขน' in line:
            obj = json.loads(line)
            c = obj.get("content", "")
            if isinstance(c, str):
                print(f"=== Step {obj.get('step_index')} ({obj.get('source')} / {obj.get('type')}) ===")
                print(c[:400])
