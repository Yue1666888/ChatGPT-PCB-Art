from pathlib import Path
import subprocess,json,sys,base64
ROOT=Path(r'D:\Users\zhangyue\Desktop\project\PCB-Art\ChatGPT-PCB-Art')
WORK=ROOT/'.tmp-work'
SESSION=json.loads((WORK/'cli-open.json').read_text(encoding='utf-8'))['value']['sessionId']
def invoke(code,timeout=75):
    p=subprocess.run([r'D:\lceda-pro\lceda-pro.exe','invoke','--session',SESSION,'--ext-uuid','eda','--code',code],capture_output=True,timeout=timeout)
    try:s=p.stdout.decode('utf-8')
    except UnicodeDecodeError:s=p.stdout.decode('gb18030',errors='replace')
    out=json.loads(s)
    if not out.get('ok'):raise RuntimeError(json.dumps(out,ensure_ascii=False))
    return out
def get_file(cache,target,size):
    chunks=[]
    for start in range(0,size,2000000):
        c=f'''const f=globalThis.{cache};if(!f)throw new Error('missing cached export');const b=new Uint8Array(await f.slice({start},{start+2000000}).arrayBuffer());let s='';for(let i=0;i<b.length;i+=32768)s+=String.fromCharCode(...b.subarray(i,i+32768));return btoa(s);'''
        r=invoke(c);chunks.append(base64.b64decode(r['value']));print('received',min(start+2000000,size),'/',size,flush=True)
    target.write_bytes(b''.join(chunks));invoke(f'delete globalThis.{cache};return true;');return target
if __name__=='__main__':
    code=Path(sys.argv[1]).read_text(encoding='utf-8');r=invoke(code)
    if len(sys.argv)>2:(WORK/sys.argv[2]).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False)[:10000])
