from pathlib import Path
import json,copy,datetime,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from inspect_project import load_records

ROOT=Path(r'D:\Users\zhangyue\Desktop\project\PCB-Art\ChatGPT-PCB-Art')
WORK=ROOT/'.tmp-work'
pcbfile=ROOT/'pcb/PCB1.epcb2'
before,errors=load_records(pcbfile)
assert not errors,errors
pcb=next(d for (kind,uid),d in before.items() if kind=='PCB')
paths=json.loads((WORK/'fabrication-paths.json').read_text(encoding='utf-8'))
oldpaths=json.loads((Path(__file__).parent/'backups/before-halo-highlights/.tmp-work/fabrication-paths.json').read_text(encoding='utf-8'))
assert paths['back-copper']==oldpaths['back-copper']
assert paths['back-open']==oldpaths['back-open']
lines=pcbfile.read_text(encoding='utf-8').splitlines()
ticket=max(json.loads(line.split('||',1)[0]).get('ticket',0) for line in lines if line.strip())
changed=[];append=[]
for name,layer in [('front-copper',1),('front-open',5)]:
    source=[r for r in pcb['records'].values() if r['head']['type']=='IMAGE' and r['data']['layerId']==layer]
    assert len(source)==1,source
    r=source[0];d=copy.deepcopy(r['data']);xs=[];ys=[]
    geom=paths[name]['paths']
    for p in geom:
        nums=[v for v in p if isinstance(v,(int,float))]
        xs.extend(nums[::2]);ys.extend(nums[1::2])
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    d.update(startX=x0,startY=y1,width=x1-x0,height=y1-y0,path=geom)
    ticket+=1;h={**r['head'],'ticket':ticket}
    append.append(json.dumps(h,separators=(',',':'))+'||'+json.dumps(d,ensure_ascii=False,separators=(',',':'))+'|\n')
    changed.append({'head':h,'data':d})
assert json.loads(lines[-1].split('||',1)[0])['type']!='DOCHEAD'
# This project ends in its PCB document. Append higher tickets so the original
# document UUID and every unrelated record stay intact.
pcbfile.write_text('\n'.join(lines)+'\n'+''.join(append),encoding='utf-8',newline='\n')
after,errors=load_records(pcbfile);assert not errors,errors
newpcb=next(d for (kind,uid),d in after.items() if kind=='PCB')
ids={r['head']['id'] for r in changed};preserved=0
for key,doc in before.items():
    assert key in after
    for uid,r in doc['records'].items():
        if uid in ids:continue
        assert r['head']==after[key]['records'][uid]['head']
        assert r['data']==after[key]['records'][uid]['data']
        preserved+=1
for r in changed:assert newpcb['records'][r['head']['id']]['data']==r['data']
index=ROOT/'ChatGPT-PCB-Art.eprj3';v=json.loads(index.read_text(encoding='utf-8'))
v['updated_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
index.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
(WORK/'new-records.json').write_text(json.dumps(changed,ensure_ascii=False),encoding='utf-8')
report={'revision':'halo-highlights','pcbUuid':newpcb['header']['uuid'],'changedLayers':[1,5],
 'changedPrimitiveIds':sorted(ids),'unrelatedRecordsPreserved':preserved,'backFabricationPathsUnchanged':True,
 'ribbonCount':11,'projectSha256':hashlib.sha256(pcbfile.read_bytes()).hexdigest()}
(WORK/'halo-project-patch.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
