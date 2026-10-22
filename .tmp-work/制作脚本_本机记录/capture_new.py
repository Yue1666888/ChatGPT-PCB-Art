from gptcli import *
import base64,json
r=invoke('''const f=await eda.dmt_EditorControl.getCurrentRenderedAreaImage();if(!f)return {captured:false};const b=new Uint8Array(await f.arrayBuffer());let s='';for(let i=0;i<b.length;i+=32768)s+=String.fromCharCode(...b.subarray(i,i+32768));return {base64:btoa(s),size:b.length};''')
v=r['value']
if 'base64' in v:
    target=ROOT/'截图/编辑器-工程画布.png';target.write_bytes(base64.b64decode(v.pop('base64')));print(target,v)
else:print(v)
