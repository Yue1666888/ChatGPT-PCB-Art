from pathlib import Path
import json,hashlib,shutil
root=Path(r'D:\Users\zhangyue\Desktop\project\PCB-Art\ChatGPT-PCB-Art')
note='''# 本机 3D 预览复核（2026-10-22）

用户截图中的预览模式为“标准丝印”，板子颜色为蓝色，焊盘喷镀为金色。此模式未显示工程里的彩色图片，因此只看到阻焊覆盖的铜轮廓和开窗露出的金属图案。

本次通过原生 CLI 查询并激活工程的 3D 预览标签，在真实客户端窗口确认“丝印工艺”为“彩色丝印”。客户端按工程两面 SILK_OPTS 的白色底色显示彩色画面，焊盘喷镀为金色。

随后在真实 3D 画布上翻转板子，复核了两面：

- 顶面：Q 版已放大为 36 mm，左侧和下侧由圆角板边裁切；主图周围有 9 颗沉金星点。本轮沿现有光晕增加 11 段断续高光弧线，几处配短伴随弧线；底下的淡紫色柔光保留彩色丝印。弧线避开人物、文字和 Q 版。
- 底面：顶部两角使用原 DeepSeek 工程的实际角花，左右镜像。手上方的小精灵保留蓝白渐变及蓝色眼睛；外圈、部分飘动线和旁边两颗小星配对增加铜与阻焊开窗。
- 本轮已修改铜和开窗几何，并重新生成工程、原生导出 EPRO2 与 Gerber。新版正反面已在本机真实 3D 预览中翻面检查。

原生实机截图：

- `截图/3D-顶面-彩色丝印-实机.png`
- `截图/3D-底面-彩色丝印-实机.png`

图片为真实客户端窗口截图，不是自制叠合模拟。顶面沿用工程竖向坐标，在截图中横向文字旋转 90°；将卡片逆时针转 90° 即为正常横向阅读。

以后打开 3D 预览时，先确认右侧“丝印工艺”显示“彩色丝印”，并确认顶面/底面板子颜色为白色、焊盘喷镀为金色。本次已调整当前预览会话；没有把会话选择宣称为已验证跨客户端重启永久生效的工程属性。

这次确认的是客户端可视化效果和整体图层对应，不代替板厂 CAM 的精细线宽与套印审核。
'''
(root/'3D预览检查说明.md').write_text(note,encoding='utf-8')
readme=root/'README.md'
s=readme.read_text(encoding='utf-8')
marker='## 原生 3D 预览补充核对'
if marker not in s:
 s+='\n\n'+marker+'\n\n已经在嘉立创客户端真实 3D 预览中检查正反面。右侧“丝印工艺”必须选择 **彩色丝印**；标准丝印模式不显示彩色原图，默认蓝色板子会造成只有轮廓和金属图案的观感。切换后两面画面与金属装饰均可正常显示。见 [3D 预览检查说明](3D预览检查说明.md) 及 `截图/3D-*-彩色丝印-实机.png`。\n'
 readme.write_text(s,encoding='utf-8')
guide=root/'实物制作指南.md';s=guide.read_text(encoding='utf-8')
if '## 在 EDA 内检查 3D 预览' not in s:
 s+='\n\n## 在 EDA 内检查 3D 预览\n\n进入 3D 标签后，在右侧属性把“丝印工艺”选择为 **彩色丝印**，检查顶面与底面板子颜色为白色，焊盘喷镀为金色。若选择“标准丝印”，工程内的真彩图片不会以本设计效果显示。预览选择和下单工艺是两个环节，下单仍需选择双面彩色丝印。\n'
 guide.write_text(s,encoding='utf-8')
html=root/'截图/双面与图层交互预览.html';s=html.read_text(encoding='utf-8')
if '3D预览检查说明.md' not in s:
 s=s.replace('<header>','<section class="card"><b>已补充真实 3D 核对</b><p>在嘉立创客户端把“丝印工艺”改为彩色丝印后，正反面的彩色人物与金属装饰均正常显示。<a href="../3D预览检查说明.md">检查说明</a> · <a href="3D-顶面-彩色丝印-实机.png">顶面实机截图</a> · <a href="3D-底面-彩色丝印-实机.png">底面实机截图</a></p></section><header>',1)
 html.write_text(s,encoding='utf-8')
for f in ['window_capture.ps1','window_click.ps1','window_orbit.ps1','activate_3d.js','inspect_3d.js','record_3d_check.py']:
 shutil.copy2(Path(__file__).parent/f,root/'.tmp-work/制作脚本_本机记录'/f)
report={'nativePreviewTabActivatedByCLI':True,'nativeClientColorSilkEnabledInCurrentSession':True,'verifiedFaces':['top','bottom'],'geometryChangedInThisCheck':True,'revisionFeatures':['11 broken ENIG halo ribbons following color glow','9 top ENIG stars','original mirrored back corner flourishes','36mm chibi cropped by rounded outline','spirit outline and partial motion trails ENIG, blue eyes kept, 2 glints'],'persistentAcrossRestartVerified':False,'evidence':['截图/3D-顶面-彩色丝印-实机.png','截图/3D-底面-彩色丝印-实机.png']}
(root/'.tmp-work/native-3d-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
manifest={str(f.relative_to(root)):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in root.rglob('*') if f.is_file() and '.tmp-work' not in f.parts}
(root/'.tmp-work/delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Native 3D evidence and preview instructions saved.')
