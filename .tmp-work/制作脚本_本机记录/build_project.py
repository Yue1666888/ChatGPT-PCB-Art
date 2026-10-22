from pathlib import Path
import sys,json,hashlib,secrets,base64,datetime,copy,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from inspect_project import load_records

SRC=Path(r'D:\Users\zhangyue\Documents\LCEDA-Pro\projects\deepseek')
ROOT=Path(r'D:\Users\zhangyue\Desktop\project\PCB-Art\ChatGPT-PCB-Art')
WORK=ROOT/'.tmp-work';ASSET=ROOT/'使用的文件'
NAME='ChatGPT-PCB-Art'
now=int(datetime.datetime.now().timestamp()*1000)
client=secrets.token_hex(8)
index=json.loads((SRC/'deepseek.eprj3').read_text(encoding='utf-8'))
profile=index['profile'];replace={}
for group in ['boards','schematics','sheets','pcbs','panels']:
    for uid in profile.get(group,{}):replace[uid]=secrets.token_hex(8)

def remap(d):
    s=json.dumps(d,ensure_ascii=False)
    for a,b in replace.items():s=s.replace(a,b)
    return json.loads(s)

index=remap(index);profile=index['profile'];index['name']=NAME
index['created_at']=index['updated_at']='2026-10-22 19:45:00'
index['default_sheet']=next(iter(profile['sheets']));index['config']['defaultSheet']=index['default_sheet'];index['pcb_count']=1
index['description']="ChatGPT dragon-girl art PCB; I've got you; 2-layer FR4, white mask, double-sided colorful silk, ENIG."
index['profile']['owner']['uuid']=str(ROOT.parent)
for name in ['sch','pcb','panel']:(ROOT/name).mkdir(exist_ok=True)
for f in (SRC/'sch').rglob('*'):
    dest=ROOT/f.relative_to(SRC)
    if f.is_dir():dest.mkdir(exist_ok=True)
    else:
        s=f.read_text(encoding='utf-8')
        for a,b in replace.items():s=s.replace(a,b)
        s=s.replace('deepseek',NAME)
        dest.write_text(s,encoding='utf-8',newline='\n')
for f in (SRC/'panel').glob('*'):
    s=f.read_text(encoding='utf-8')
    for a,b in replace.items():s=s.replace(a,b)
    (ROOT/'panel'/f.name).write_text(s,encoding='utf-8',newline='\n')
ecfg=ROOT/'sch/Schematic1/Schematic1.ecfg'
(ROOT/'sch/Schematic1/Schematic1.evar').write_text('',encoding='utf-8')

source_docs,_=load_records(SRC/'pcb/PCB1.epcb2')
pcb=next(d for (k,u),d in source_docs.items() if k=='PCB')
newpcbuid=replace[pcb['header']['uuid']]
paths=json.loads((WORK/'fabrication-paths.json').read_text(encoding='utf-8'))

records=[];new_records=[];ticket=0
def record(t,d,uid=None,track=False):
    global ticket
    ticket+=1
    h={'type':t,'ticket':ticket}
    if t!='DOCHEAD':h['id']=uid if uid is not None else secrets.token_hex(8)
    records.append(json.dumps(h,separators=(',',':'))+'||'+json.dumps(d,ensure_ascii=False,separators=(',',':'))+'|\n')
    if track:new_records.append({'head':h,'data':d})
    return h.get('id')

def dochead(kind,uid):
    return {'docType':kind,'client':client,'uuid':uid,'updateTime':now,'version':str(now),'editVersion':'4.1.60'}

record('DOCHEAD',dochead('BLOB','BLOB'))
blobs={}
for filename in ['顶面主图_板面坐标_4K.jpg','顶面Q版_板面坐标_4K.png','底面主图_完整板面_4K.jpg']:
    raw=(ASSET/filename).read_bytes();mime='image/jpeg' if filename.endswith('.jpg') else 'image/png'
    content=f'data:{mime};base64,'+base64.b64encode(raw).decode('ascii')
    uid=hashlib.sha256(content.encode()).hexdigest();blobs[filename]=uid
    record('BLOB',{'filename':filename,'content':content},uid,track=True)
record('DOCHEAD',dochead('PCB',newpcbuid))
rs=[r for r in pcb['records'].values() if r['data'] is not None]
canvas=next(r for r in rs if r['head']['type']=='CANVAS')
record('CANVAS',canvas['data'],'CANVAS')
keep={'META','PRIMITIVE','LAYER','LAYER_PHYS','RULE_TEMPLATE','RULE','NET','SILK_OPTS','PREFERENCE','PANELIZE','ACTIVE_LAYER'}
for r in rs:
    h,d=r['head'],r['data']
    if h['type'] not in keep:continue
    d=remap(d)
    if h['type']=='ACTIVE_LAYER':d={'layerId':1}
    if h['type']=='META':d['title']='PCB1'
    record(h['type'],d,h.get('id'))

def mil(mm):return round(mm/.0254,5)
outline={'partitionId':'','groupId':0,'netName':'','layerId':11,'width':10,'path':['R',0,0,mil(60),mil(100),0,mil(4)],'locked':False,'zIndex':-1,'polyType':'BOARD_OUTLINE'}
record('POLY',outline,track=True)
def obj(filename,layer,x,y,w,h):
    d={'partitionId':'','groupId':0,'layerId':layer,'fileName':filename,'startX':mil(x),'startY':-mil(y),'width':mil(w),'height':mil(h),'angle':0,'mirror':False,'path':'blob:'+blobs[filename],'locked':False,'zIndex':-1}
    record('OBJ',d,track=True)
obj('顶面主图_板面坐标_4K.jpg',3,0,0,60,100)
obj('顶面Q版_板面坐标_4K.png',3,-5,-4,36,36)
# The bottom-side anchor is at board-right, matching the editor's side transform.
obj('底面主图_完整板面_4K.jpg',4,60,0,60,100)
for name,layer in [('front-copper',1),('front-open',5),('back-copper',2),('back-open',6)]:
    geom=paths[name]['paths'];xs=[];ys=[]
    for p in geom:
        nums=[v for v in p if isinstance(v,(int,float))]
        xs.extend(nums[::2]);ys.extend(nums[1::2])
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    anchorX=mil(60)-x0 if layer in (2,6) else x0
    d={'partitionId':'','groupId':0,'layerId':layer,'startX':anchorX,'startY':y1,'width':x1-x0,'height':y1-y0,'angle':0,'mirror':False,'path':geom,'locked':False,'zIndex':-1}
    record('IMAGE',d,track=True)

(ROOT/f'{NAME}.eprj3').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
(ROOT/'pcb/PCB1.epcb2').write_text(''.join(records),encoding='utf-8',newline='\n')
(WORK/'new-records.json').write_text(json.dumps(new_records,ensure_ascii=False),encoding='utf-8')
(WORK/'project-build.json').write_text(json.dumps({'source':str(SRC),'output':str(ROOT),'pcbUuid':newpcbuid,'client':client,'recordCount':len(records),'newRecords':len(new_records),'drawingObjects':8,'geometry':{k:{a:b for a,b in v.items() if a!='paths'} for k,v in paths.items()}},ensure_ascii=False,indent=2),encoding='utf-8')
print('Built',ROOT,'PCB bytes',(ROOT/'pcb/PCB1.epcb2').stat().st_size)
