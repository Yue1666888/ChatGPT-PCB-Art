from pathlib import Path
import sys,json,zipfile,io,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from render_gerber import gerber_svg_elements,wrap
from PIL import Image,ImageChops,ImageFilter
import pymupdf as fitz
ROOT=Path(r'D:\Users\zhangyue\Desktop\project\PCB-Art\ChatGPT-PCB-Art');WORK=ROOT/'.tmp-work';SHOT=ROOT/'截图'
names={1:'Gerber_TopLayer.GTL',2:'Gerber_BottomLayer.GBL',5:'Gerber_TopSolderMaskLayer.GTS',6:'Gerber_BottomSolderMaskLayer.GBS'}
z=zipfile.ZipFile(ROOT/'Gerber_PCB1_2026-10-22.zip')
for n in names.values():(WORK/n).write_bytes(z.read(n))
def raster(svg):
    doc=fitz.open(stream=svg.encode(),filetype='svg');pix=doc[0].get_pixmap(matrix=fitz.Matrix(2,2))
    return Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
metrics={};masks={}
for lid,n in names.items():
    body,stats=gerber_svg_elements(WORK/n,'white')
    mask=raster(wrap(body,mirror=lid in (2,6),bg='black')).convert('L')
    masks[lid]=mask
    visual=raster(wrap(body.replace('fill="white"','fill="#b68b32"').replace('stroke="white"','stroke="#b68b32"'),mirror=lid in (2,6)))
    if lid in (1,5):visual=visual.transpose(Image.Transpose.ROTATE_90)
    visual.save(SHOT/f'图层-{lid}-Gerber.png')
    if lid in (1,5):mask=mask.transpose(Image.Transpose.ROTATE_90)
    refname={1:'front-copper-white.png',5:'front-open-white.png',2:'back-copper-white.png',6:'back-open-white.png'}[lid]
    ref=Image.open(WORK/refname).convert('L').resize(mask.size,Image.Resampling.LANCZOS)
    mask=mask.point(lambda p:255 if p>100 else 0);ref=ref.point(lambda p:255 if p>100 else 0)
    inter=sum(ImageChops.darker(mask,ref).getdata())/255
    union=sum(ImageChops.lighter(mask,ref).getdata())/255
    nearNative=mask.filter(ImageFilter.MaxFilter(5));nearRef=ref.filter(ImageFilter.MaxFilter(5))
    sourceCoverage=sum(ImageChops.darker(ref,nearNative).getdata())/max(1,sum(ref.getdata()))
    nativeCoverage=sum(ImageChops.darker(mask,nearRef).getdata())/max(1,sum(mask.getdata()))
    metrics[str(lid)]={**stats,'intended_vs_native_iou':round(inter/union,5),'coverage_within_0_1mm':{'source':round(sourceCoverage,6),'native':round(nativeCoverage,6)},'source':n}
for side,c,m in [('front',1,5),('back',2,6)]:
    expose=ImageChops.darker(masks[c],masks[m])
    if side=='front':expose=expose.transpose(Image.Transpose.ROTATE_90)
    expose.save(WORK/(side+'-native-gold-mask.png'))
    vis=Image.new('RGB',expose.size,'white');vis.paste('#c29b42',(0,0,*vis.size),expose);vis.save(SHOT/('图层-'+side+'-实际露铜交集.png'))
expected={'Fabrication_ColorfulTopSilkscreen.FCTS','Fabrication_ColorfulBottomSilkscreen.FCBS','Gerber_TopLayer.GTL','Gerber_BottomLayer.GBL','Gerber_TopSolderMaskLayer.GTS','Gerber_BottomSolderMaskLayer.GBS','Gerber_BoardOutlineLayer.GKO'}
report={'gerber_files':{i.filename:i.file_size for i in z.infolist()},'required_files_present':expected.issubset(z.namelist()),'layers':metrics,'ordinary_silk_has_drawing':any('D01*' in z.read(n).decode('ascii') for n in ['Gerber_TopSilkscreenLayer.GTO','Gerber_BottomSilkscreenLayer.GBO'])}
report['geometry_matches']=all(m['intended_vs_native_iou']>.90 for m in metrics.values())
(WORK/'native-gerber-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
if not report['geometry_matches'] or not report['required_files_present']:raise SystemExit(1)
