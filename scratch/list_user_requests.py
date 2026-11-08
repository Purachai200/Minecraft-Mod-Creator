import sys, json
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\Purachai\.gemini\antigravity\brain\dc63a5aa-ae1e-416f-8afe-779a698ca425\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get('source') == 'USER_EXPLICIT':
            c = obj.get('content', '')
            print(f"Step {obj.get('step_index')}: {c}\n---")
