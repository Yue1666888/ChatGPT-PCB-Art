from gptcli import *
import time,zipfile

def export(kind,cache,filename):
    if kind=='gerber':code=f"globalThis.{cache}=await eda.pcb_ManufactureData.getGerberFile('ChatGPT-PCB-Art',true);return {{available:!!globalThis.{cache},size:globalThis.{cache}?.size}};"
    else:code=f"globalThis.{cache}=await eda.sys_FileManager.getProjectFile('ChatGPT-PCB-Art',undefined,'epro2');return {{available:!!globalThis.{cache},size:globalThis.{cache}?.size}};"
    r=invoke(code,timeout=90);print(kind,json.dumps(r),flush=True)
    (WORK/f'{kind}-export.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    if not r['value'].get('available'):raise RuntimeError('Empty '+kind+' export')
    target=get_file(cache,ROOT/filename,r['value']['size'])
    with zipfile.ZipFile(target) as z:print('verified archive',target.name,len(z.namelist()),flush=True)
    return target

if __name__=='__main__':
    export('gerber','__gptArtGerber','Gerber_PCB1_2026-10-22.zip')
    export('epro2','__gptArtProject','ProPrj_ChatGPT_2026-10-22.epro2')
