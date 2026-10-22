from pathlib import Path
import json,base64,shutil,hashlib,zipfile
ROOT=Path(r'D:\Users\zhangyue\Desktop\project\PCB-Art\ChatGPT-PCB-Art')
WORK=ROOT/'.tmp-work';SHOT=ROOT/'截图';LOCAL=Path(__file__).parent
section='''## 光晕高光更新

顶面人物周围的淡紫色光晕仍由彩色丝印呈现，在光环上新增 11 段断续沉金曲线，含长弧及较短的伴随弧。局部宽度变化形成水波高光的节奏，避开人物、文字与 Q 版。

弧线同时写入顶铜层（1 / GTL）和顶层阻焊开窗（5 / GTS）；铜与开窗重合的区域按沉金方案呈现金属反光。柔光渐变由原彩印保留，开窗只负责曲线金属高光。

本次保留原工程文档 UUID 与图元 ID，仅更新顶铜、顶层阻焊开窗两个图元。底面角花、精灵、人物与彩色图片保留。已重新导出 `.epro2` 与 Gerber，并更新交互预览和真实客户端 3D 截图。

高光弧线矢量：`使用的文件/顶面光晕_断续沉金高光.svg`。位置和宽度参数记录在 `.tmp-work/layout.json`；实际制造图层核对记录见 `.tmp-work/halo-native-audit.json`。
'''
for name in ['README.md','本轮修改说明.md']:
    p=ROOT/name;s=p.read_text(encoding='utf-8')
    if '## 光晕高光更新' in s:s=s.split('## 光晕高光更新')[0].rstrip()
    p.write_text(s+'\n\n'+section,encoding='utf-8')
p=ROOT/'实物制作指南.md';s=p.read_text(encoding='utf-8')
if '## 光晕高光图层' not in s:
    s+='\n\n## 光晕高光图层\n\n顶面的断续光晕曲线同时存在于 GTL 与 GTS 中，配合沉金工艺呈现金属反光。淡紫色渐变与散光保留在 FCTS 彩色丝印中。请在工厂生产稿中同时检查这三层的对应关系。\n'
    p.write_text(s,encoding='utf-8')
p=SHOT/'双面与图层交互预览.html';s=p.read_text(encoding='utf-8')
start=s.index('const modes=')+len('const modes=');end=s.index(';const box=',start)
modes=json.loads(s[start:end])
files={'effect':('预览-顶面-双图与金属文字.png','预览-底面-上中身与金属描边.png'),
 'color':('front-仅彩印.png','back-仅彩印.png'),'copper':('图层-1-Gerber.png','图层-2-Gerber.png'),
 'open':('图层-5-Gerber.png','图层-6-Gerber.png'),'gold':('图层-front-实际露铜交集.png','图层-back-实际露铜交集.png')}
for mode,(f,b) in files.items():
    for side,name in [('front',f),('back',b)]:modes[mode][side]='data:image/png;base64,'+base64.b64encode((SHOT/name).read_bytes()).decode('ascii')
modes['effect']['text']='两面彩图与本次原生 Gerber 露铜交集叠合。顶面新增11段断续光晕高光；金色为工艺示意，不模拟实物反射。'
modes['open']['text']='顶面：文字、9颗星点、11段光晕曲线、饰物与角框；底面：原工程角花、精灵轮廓、2颗小星及人物局部描边。'
s=s[:start]+json.dumps(modes,ensure_ascii=False)+s[end:]
if '11 段断续光晕高光' not in s:s=s.replace('<h1>I\'ve got you.</h1>','<h1>I\'ve got you.</h1><p><b>本版新增：</b>11 段断续光晕高光，沿彩印光环分布，配对写入顶铜与阻焊开窗。</p>',1)
p.write_text(s,encoding='utf-8')
for pattern in ['*.py','*.cjs','*.ps1','*.js']:
    for p in LOCAL.glob(pattern):shutil.copy2(p,WORK/'制作脚本_本机记录'/p.name)
for name in ['ProPrj_ChatGPT_2026-10-22.epro2','Gerber_PCB1_2026-10-22.zip']:
    with zipfile.ZipFile(ROOT/name) as z:assert z.testzip() is None;print(name,'CRC OK',len(z.namelist()))
patch=json.loads((WORK/'halo-project-patch.json').read_text(encoding='utf-8'))
build=json.loads((WORK/'project-build.json').read_text(encoding='utf-8'))
paths=json.loads((WORK/'fabrication-paths.json').read_text(encoding='utf-8'))
build['geometry']={k:{n:v for n,v in d.items() if n!='paths'} for k,d in paths.items()}
build['latestRevision']=patch
(WORK/'project-build.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf-8')
manifest={str(f.relative_to(ROOT)):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in ROOT.rglob('*') if f.is_file() and '.tmp-work' not in f.parts}
(WORK/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Updated halo notes, interactive layers and scripts')
