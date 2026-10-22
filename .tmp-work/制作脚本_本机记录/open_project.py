from pathlib import Path
import subprocess,json
ROOT=Path(r'D:\Users\zhangyue\Desktop\project\PCB-Art\ChatGPT-PCB-Art')
target=ROOT/'ChatGPT-PCB-Art.eprj3'
p=subprocess.run([r'D:\lceda-pro\lceda-pro.exe','open','--path',str(target)],capture_output=True,timeout=50)
raw=p.stdout.decode('utf-8',errors='replace');print(raw)
out=json.loads(raw);(ROOT/'.tmp-work/cli-open.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
if not out.get('ok'):raise SystemExit(1)
