from pathlib import Path
import shutil,json,hashlib,html,base64,zipfile,datetime

ROOT=Path(r'D:\Users\zhangyue\Desktop\project\PCB-Art\ChatGPT-PCB-Art')
SRC=Path(r'D:\Users\zhangyue\Desktop\project\PCB-Art\DeepSeek-PCB-Art')
LOCAL=Path(__file__).resolve().parent
ASSET=ROOT/'使用的文件';WORK=ROOT/'.tmp-work';SHOT=ROOT/'截图'
shutil.copy2(SRC/'LICENSE',ROOT/'LICENSE')
ref=ASSET/'原始参考';ref.mkdir(exist_ok=True)
for src,name in [
 (r'D:\Users\zhangyue\Downloads\gpt-dragon-niang-bust.png','原始参考-Q版龙娘.png'),
 (r'D:\Users\zhangyue\Downloads\e4565384e7e5b2d75756e577f505534b4168597.png','原始参考-伸手龙娘.png'),
 (r'D:\Users\zhangyue\Downloads\6e1c4e1bf7889d4da8455316b616c24b4168597.jpg@1052w_!web-dynamic.avif','原始参考-竖版龙娘.avif')]:shutil.copy2(src,ref/name)
scripts=WORK/'制作脚本_本机记录';scripts.mkdir(exist_ok=True)
for f in LOCAL.glob('*.py'):shutil.copy2(f,scripts/f.name)
for f in LOCAL.glob('*.cjs'):shutil.copy2(f,scripts/f.name)
shutil.copy2(LOCAL/'package.json',scripts/'package.json')

readme='''# ChatGPT Dragon Girl PCB Art — I've got you

双面 ChatGPT 龙娘 PCB 艺术卡片。基于 DeepSeek-PCB-Art 的板框和工艺组织方式制作，替换了两面画面及金属装饰，原 DeepSeek 工程未改动。

**先看效果：[双面与图层交互预览](截图/双面与图层交互预览.html)。** 金色在预览中采用示意色，图形依据本工程的原生 Gerber 铜与阻焊开窗交集；不等同于实物反光或工厂 FCTS/FCBS 专用彩印预览。

## 成品规格

| 项目 | 设计 |
|---|---|
| 外形 | 60 × 100 mm，R4 mm 圆角；顶面按横向 100 × 60 mm 阅读 |
| 结构 | 2 层铜，FR4，工程厚度模型约 1.6 mm，上下铜约 35 μm |
| 工艺方案 | 白色阻焊、双面嘉立创彩色丝印、露铜沉金 |
| 电路 | 无元件、焊盘、过孔或电气功能 |
| 顶面 | 左下 Q 版龙娘；右侧伸手龙娘；左上金属字 `I've got` / `you` |
| 底面 | 竖向龙娘上中身，保留胸前手势、向外伸出的手及浮游精灵；腿脚不作为构图重点 |

顶面对应 EDA 的 1/3/5 层，底面对应 2/4/6 层。板子坐标保持竖向；将顶面逆时针转 90° 即为横向阅读方向。底面预览已按从底面观察的方向处理。

## 文件结构

```text
ChatGPT-PCB-Art/
├─ ChatGPT-PCB-Art.eprj3             # 直接打开这个文件，可编辑
├─ pcb/PCB1.epcb2                   # PCB 图形、嵌入图片和配置
├─ sch/Schematic1/                  # 默认空白图框，没有实际电路
├─ panel/Panel1.epan2               # 空面板占位，不启用拼板
├─ ProPrj_ChatGPT_2026-10-22.epro2   # 嘉立创客户端原生导出的单文件工程包
├─ Gerber_PCB1_2026-10-22.zip        # 嘉立创客户端原生制造包
├─ 使用的文件/                      # AI 原生图、4096px 制作稿、板面图、原始参考
├─ 截图/                            # 双面预览、真实 Gerber 图层、编辑器截图
├─ .tmp-work/                       # 制作中间数据、图形路径、校验与 CLI 记录
├─ 实物制作指南.md
├─ LICENSE
└─ README.md
```

不要单独移动 `.eprj3` 索引：文件夹工程需要连同 `pcb/`、`sch/` 和 `panel/` 一起保存。若要只发送一个工程文件，使用 `.epro2`。

## 三张素材的高清处理

三张用户素材均先使用内置 image_gen 重绘，再制作板面图。生成工具实际原生输出没有达到 4K，以下 4096px 文件是**AI 重绘后以 Lanczos3 重采样的制作稿**，不标称原生 4K 或新增了等量原始细节。原生重绘文件也全部保留。

| 文件 | AI 原生像素 | 制作稿像素 |
|---|---:|---:|
| ChatGPT_chibi_4K.png | 1254 × 1254 | 4096 × 4096，保留透明通道 |
| ChatGPT_front_4K.jpg | 1672 × 941 | 4096 × 2305 |
| ChatGPT_back_4K.jpg | 972 × 1619 | 2459 × 4096 |

工程实际使用 `顶面主图_板面坐标_4K.jpg`、`顶面Q版_板面坐标_4K.png` 与 `底面主图_完整板面_4K.jpg`。主图已经按板面旋转/裁切，Q 版仍为独立对象。完整使用参数见 `.tmp-work/layout.json`；重绘提示词见 `使用的文件/重绘提示词.md`。

## 图层如何配合

| 层 | 图形 | 工艺用途 |
|---|---|---|
| 1 顶铜 | 伸手龙娘主图轮廓、金属文字、星形及角框 | 铜面形状；部分线条藏在阻焊下面 |
| 3 顶丝印 | 主图 + 独立 Q 版，共 2 个彩色 OBJ | 顶面彩印，输出 FCTS |
| 5 顶阻焊 | `I've got you`、星形、角框、头饰和腰饰局部轮廓 | 开窗后露铜；选择沉金呈现金色 |
| 2 底铜 | 龙娘上中身矢量轮廓、饰物和角框 | 铜面形状 |
| 4 底丝印 | 竖向上中身板面图，1 个彩色 OBJ | 底面彩印，输出 FCBS |
| 6 底阻焊 | 龙角、发丝、饰物、衣褶、尾部与角框等轮廓；脸和手势部分保留彩色 | 开窗后露铜；避免把大面积面部和手变成金属色 |
| 11 板框 | 圆角矩形 | 锣边外形 |

可见金属的基本几何条件是 `铜图形 ∩ 阻焊开窗`。沉金是露铜表面的处理，不是一张额外铜层。工程没有单独的“金色油墨层”。普通 GTO/GBO 为空，彩色原图放在 FCTS/FCBS 专用制造文件中；文字来自铜和开窗的矢量字形。

制作时对线稿做了小杂点过滤、描边扩展与矢量化，并为金属图形设置约 0.5 mm 的外缘保留。铜图案和开窗分别存储，均由同一板面坐标构建。原生 Gerber 的几何渲染与设计图已经对照，校验数据保存在 `.tmp-work/native-gerber-audit.json`；它是图形核对记录，不是板厂 CAM 审核或精密工艺能力报告。

## 打开与生产文件

直接用嘉立创 EDA 专业版打开 `ChatGPT-PCB-Art.eprj3`。另一种方式是在客户端通过“导入嘉立创 EDA 专业版”导入 `.epro2`。

制造包包含 GTL/GBL、GTS/GBS、GKO 和双面 FCTS/FCBS。不能丢弃两个彩色专用文件，否则主画面不会按本设计生产。下单选择白色阻焊、沉金、双面嘉立创彩色丝印，详见《实物制作指南》。本次未提交生产订单，实际金厚与生产套印能力由订单和板厂确认。

## 已完成的核对

- 新工程已被嘉立创 EDA 4.1.60 原生 CLI 打开，并返回正确的工程树、2 层铜、0 焊盘与 0 过孔。
- 新生成的 11 条 BLOB/OBJ/IMAGE/板框记录完成官方格式库检查。未分组 `groupId=0` 按官方字段说明与真实客户端处理；旧 schema 的字符串类型偏差仅在检查投影中兼容，不改写工程数值。
- 修正了底面自动镜像下的锚点，以及矢量孔洞的轮廓方向；以修正版重新导出工程和 Gerber。
- 原生 Gerber 的铜、开窗、板框和双面彩印文件均存在；两份 ZIP/EPRO2 归档 CRC 检查通过。
- 附带的旧版目录级 `easyeda-eprj3/validate.js` 仅识别无 ticket 的 DOCHEAD，在真实客户端带 ticket 的文件上会崩溃，未将该脚本运行计为通过。实际完成依据是记录检查、客户端解析和原生制造导出。

## 来源与署名

板框、基础工程组织和工艺方法参考同目录 `DeepSeek-PCB-Art`；保留其 LICENSE，原上游为 alsunmengy/DeepSeek-PCB-Art，用户已有修订版为 spasmodiczz。人物素材由用户提供，三张 AI 重绘与新排版在本次制作中生成。保留源协议不等于重新授予原始人物素材或品牌标志的权利。
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')

guide='''# ChatGPT 艺术板实物制作指南

## 推荐提交文件

使用本目录的 `Gerber_PCB1_2026-10-22.zip`。它是本工程在嘉立创 EDA 专业版中原生导出的制造包，包含双面彩色丝印专用文件。

需要修改图案时，先打开完整 `.eprj3` 文件夹工程或导入 `.epro2`，改完再重新导出。工程与制造包不是同一种用途。

## 参数

| 设置 | 本设计对应值 |
|---|---|
| 板材 | FR-4 |
| 层数 | 2 层 |
| 成品尺寸 | 60 × 100 mm，R4 圆角 |
| 板厚 | 1.6 mm |
| 外层铜厚 | 1 oz / 约 35 μm 的目标方案 |
| 阻焊 | 白色 |
| 表面处理 / 焊盘喷镀 | 沉金；金厚按下单页面实际可选参数确定 |
| 字符工艺 | 嘉立创彩色丝印，双面 |
| 数量 | 按需要选择；本次未下单 |
| 拼板 / SMT / 钢网 | 本工程未设计拼板，也没有焊接需求 |

彩色印刷与沉金配合时，人物颜色来自彩色丝印，金属字、局部饰物与线稿来自开窗后的露铜沉金。不要把沉金改成普通喷锡，否则金色区域会变为银色等其他表面效果。

## 下单前看这几处

1. 压缩包内必须保留 `Fabrication_ColorfulTopSilkscreen.FCTS` 和 `Fabrication_ColorfulBottomSilkscreen.FCBS`。
2. 顶面横向阅读：Q 版在左下，主图在右，左上是 `I've got` / `you`。确认撇号、字母孔洞及金属字都正确。
3. 底面按从底面正视的方向看：保留向外的手和浮游精灵，人物以头部到上中身为主。
4. 铜层与开窗层一起检查：顶面文字和饰物、底面发丝/服饰线稿应与彩色图位置对应。
5. 确认圆角板框尺寸，以及生产稿中是否有额外客编/订单标记占用画面。
6. 本次完成了文件与图形核对；精细线稿在生产时的最小线宽、细小孤岛处理与套印效果，需按板厂 CAM 生产稿确认。

本板没有电气功能，工程无元件、焊盘、过孔和实际电路。导出包出现钻孔图或飞针数据的辅助文件，不代表本板设计了电气连接或钻孔。

## 本机文件检查

`.tmp-work/primitive-validation.json` 保存新记录校验结果；`.tmp-work/editor-inventory.json` 保存客户端解析结果；`.tmp-work/native-gerber-audit.json` 保存制造层图形对照。截图中的金色为示意，实物具有金属反光，印刷色也可能与屏幕有差别。
'''
(ROOT/'实物制作指南.md').write_text(guide,encoding='utf-8')

prompts='''# 图像重绘提示词与输出说明

工具：内置 image_gen；3 次独立的参考图编辑。工具原生返回约 1.6MP，后以 Lanczos3 导出 4096px 长边制作稿；AI 原生版本同时归档。以下为本次提示词的制作规格摘要，未另行使用收费图像 API。

## 1. Q 版龙娘

Identity-preserving high-resolution illustration restoration. Preserve the exact chibi bust composition, white/lavender hair, two pale segmented dragon horns, pointed ears, sleepy large lavender eyes, heavy dark eyebrows, neutral mouth and blush. Preserve the interwoven ChatGPT-inspired knot ornament and diamond tassel on viewer-right, white/lavender dress and two shoulders. Crisp linework, clean damaged bottom edge and edge fringes; keep complete horns and hair with transparent margin. Genuine transparent background. No lettering, no additional characters, no watermark. Requested 4096×4096.

## 2. 顶面主图

Remaster the exact reference as a high-detail landscape anime illustration. Preserve white-haired lavender-eyed dragon woman, segmented pale horns, pointed ears, knot hair ornament, flowing white/lavender fantasy dress, one arm reaching toward viewer-left and the other near the chest, tail, pale lilac luminous backdrop and tiny stars. Keep the woman on the right two-thirds and generous pale space on the left for a separate chibi and lettering. Entire reaching hand within frame. Horns to roughly mid-thigh, no feet needed. No text or watermark or PCB mockup. Requested native 4K 3840×2160.

## 3. 底面主图

Identity-preserving composition edit for a portrait art-card back, requested 2458×4096 and aspect 3:5. Preserve the exact adult white-haired lavender-eyed dragon woman, horns, ears, knot ornaments, fantasy dress, sleeve drapes, necklace and tail. Preserve viewer-left hand near chest and other forearm/hand toward viewer-right with the small pale-blue two-eyed floating spirit above it. Show upper/middle body; minimize left empty space, shift torso left and subtly tilt about 5 degrees if needed to make room for the outward arm. Keep horns, reaching hand and spirit in frame; no legs or feet required. Near-white backdrop with faint lilac glow, clean linework suitable for metallic contours. No lettering, border, watermark, extra characters or mockup.
'''
(ASSET/'重绘提示词.md').write_text(prompts,encoding='utf-8')

def data(name):
    f=SHOT/name;return 'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode()
modes={
 'effect':{'label':'叠合效果','front':data('预览-顶面-双图与金属文字.png'),'back':data('预览-底面-上中身与金属描边.png'),'text':'两面图案与实际 Gerber 露铜交集叠合。金色是工艺示意，不模拟金属反射与工厂套印。'},
 'color':{'label':'彩色丝印','front':data('front-仅彩印.png'),'back':data('back-仅彩印.png'),'text':'顶面主图与独立 Q 版组成双图卡面；底面是裁到上中身的竖向人物。'},
 'copper':{'label':'铜图形','front':data('图层-1-Gerber.png'),'back':data('图层-2-Gerber.png'),'text':'从本次原生 Gerber 渲染的顶铜与底铜。铜上有线稿，不代表这些区域全部会露金。'},
 'open':{'label':'阻焊开窗','front':data('图层-5-Gerber.png'),'back':data('图层-6-Gerber.png'),'text':'这些图案对应不盖白油的位置。顶面以文字和饰物为主；底面保留更多龙角、发丝与服饰线稿。'},
 'gold':{'label':'实际露铜交集','front':data('图层-front-实际露铜交集.png'),'back':data('图层-back-实际露铜交集.png'),'text':'按铜 ∩ 开窗计算的区域。下单选择沉金时，这些区域按表面处理呈现金属效果。'}
}
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ChatGPT PCB Art · I've got you</title><style>*{box-sizing:border-box}body{margin:0;background:#f2f0f8;color:#322d45;font:16px/1.8 "Microsoft YaHei",system-ui,sans-serif}main{max-width:1350px;margin:auto;padding:36px 28px}h1{font-size:38px;line-height:1.3;margin:8px 0 16px}.tag{letter-spacing:.12em;font-size:12px;color:#765e99;font-weight:700}.card{background:white;border:1px solid #dfd8e9;border-radius:18px;padding:23px;margin:25px 0}button{background:white;border:1px solid #d7cce1;padding:9px 17px;border-radius:8px;font:inherit;font-size:14px;cursor:pointer;margin:0 6px 8px 0}button[aria-pressed=true]{background:#5d477c;color:white}#note{font-size:14px;color:#74677d;min-height:45px}.faces{display:grid;grid-template-columns:1.65fr 1fr;gap:28px;align-items:start}.faces img{width:100%;display:block;box-shadow:0 12px 28px #32244518;border-radius:15px}.faces p{font-size:14px;color:#74677d;margin:7px 0 14px}.pill{display:inline-block;border:1px solid #dfd8e9;background:white;padding:4px 12px;border-radius:30px;font-size:13px;margin:0 7px 8px 0}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:11px;text-align:left;border-bottom:1px solid #e8e1ee}a{color:#60448c}.small{font-size:13px;color:#74677d}h2{font-size:21px}.cols{display:grid;grid-template-columns:1fr 1fr;gap:24px}@media(max-width:800px){main{padding:24px 14px}.faces,.cols{grid-template-columns:1fr}h1{font-size:29px}.faces img{max-height:760px;object-fit:contain;box-shadow:none}.card{padding:15px}table{font-size:12px}th,td{padding:7px}}</style><main><header><div class="tag">CHATGPT PCB ART · 2026.10.22</div><h1>I've got you.</h1><p>白发龙娘的双面艺术卡片。顶面横向构图：左下 Q 版、右侧主图；底面竖向构图：上中身与伸手姿态。金属字与局部轮廓通过铜和阻焊开窗实现。</p><span class="pill">60 × 100 mm · R4</span><span class="pill">FR4 · 2 层铜</span><span class="pill">白色阻焊 · 双面彩印 · 沉金方案</span><span class="pill">原生 CLI 已打开并导出</span></header><section class="card"><div id="buttons"></div><p id="note"></p><div class="faces"><div><b>顶面 · 横向阅读</b><p>I've got you / Q 版龙娘 / 伸手龙娘</p><img id="front" alt="顶面图案"></div><div><b>底面 · 竖向阅读</b><p>龙角、白发、饰物与衣褶的金属描边</p><img id="back" alt="底面图案"></div></div></section><section class="card"><h2>图层与工艺的配合</h2><table><tr><th>面</th><th>铜层</th><th>彩色丝印</th><th>阻焊开窗</th></tr><tr><td>顶面</td><td>1 / GTL：主图轮廓、字形、星形与角框</td><td>3 / FCTS：主图 + Q 版</td><td>5 / GTS：字形、星形、角框、局部头饰腰饰</td></tr><tr><td>底面</td><td>2 / GBL：上中身整体线稿与角框</td><td>4 / FCBS：竖向上中身画面</td><td>6 / GBS：龙角、发丝、饰物、衣褶等；面部与手势保留彩印</td></tr></table><p>露铜条件为 <b>铜图形 ∩ 阻焊开窗</b>。沉金是露铜表面的处理，金色并非画在 RGB 图片中的油墨层。实际金厚和生产套印以订单与板厂生产稿为准。</p></section><section class="card"><h2>文件与图像说明</h2><div class="cols"><div><p><a href="../ChatGPT-PCB-Art.eprj3">打开文件夹工程 .eprj3</a><br><a href="../ProPrj_ChatGPT_2026-10-22.epro2">单文件工程 .epro2</a><br><a href="../Gerber_PCB1_2026-10-22.zip">原生 Gerber 制造包</a><br><a href="../README.md">完整说明</a> · <a href="../实物制作指南.md">实物制作指南</a></p></div><div><p class="small">三张素材均经内置图像工具重绘。工具实际原生输出约 1.6MP，4096px 制作稿为重绘后的 Lanczos3 重采样导出，原生重绘图同时保留，不标称原生 4K。尺寸分别为 4096×4096、4096×2305、2459×4096。</p><p class="small">本页为工艺示意；已用本次原生 Gerber 重建金属区域，不能替代工厂专用 FCTS/FCBS 预览或实物反光。本次没有下单。</p></div></div></section><p class="small">本页离线可用。源工程与原始参考保留；新工程和全部素材已输出到 ChatGPT-PCB-Art。<a href="../.tmp-work/native-gerber-audit.json">查看制造图层核对记录</a></p></main><script>const modes=__MODES__;const box=document.getElementById('buttons');for(const[k,v]of Object.entries(modes)){const b=document.createElement('button');b.textContent=v.label;b.dataset.mode=k;b.onclick=()=>show(k);box.append(b)}function show(k){const v=modes[k];document.getElementById('front').src=v.front;document.getElementById('back').src=v.back;document.getElementById('note').textContent=v.text;document.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.mode===k?'true':'false'))}show('effect');</script></html>'''
(SHOT/'双面与图层交互预览.html').write_text(page.replace('__MODES__',json.dumps(modes,ensure_ascii=False)),encoding='utf-8')

# Remove only rejected exports generated in this task; none are part of delivery.
reject=(WORK/'rejected-v1').resolve()
assert reject.parent==WORK.resolve()
if reject.exists():shutil.rmtree(reject)
large=WORK/'new-records.json'
if large.exists():large.unlink()
manifest={}
for f in ROOT.rglob('*'):
    if f.is_file() and '.tmp-work' not in f.parts:manifest[str(f.relative_to(ROOT))]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(WORK/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Packaged',len(manifest),'deliverables at',ROOT)
print('Interactive preview bytes',(SHOT/'双面与图层交互预览.html').stat().st_size)
