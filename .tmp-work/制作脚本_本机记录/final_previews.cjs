const fs=require('fs'),path=require('path'),sharp=require('sharp');
const {Resvg}=require('@resvg/resvg-js');
const root='D:/Users/zhangyue/Desktop/project/PCB-Art/ChatGPT-PCB-Art',wdir=path.join(root,'.tmp-work'),shots=path.join(root,'截图');
(async()=>{
 for(const [side,input,mask,w,h,name]of [
 ['front','front-color-landscape.png','front-native-gold-mask.png',2000,1200,'预览-顶面-双图与金属文字.png'],
 ['back','back-color-portrait.png','back-native-gold-mask.png',1200,2000,'预览-底面-上中身与金属描边.png']]){
   const alpha=await sharp(path.join(wdir,mask)).resize(w,h,{kernel:'lanczos3'}).greyscale().raw().toBuffer();
   const gold=await sharp({create:{width:w,height:h,channels:3,background:'#c29b42'}}).joinChannel(alpha,{raw:{width:w,height:h,channels:1}}).png().toBuffer();
   const svg=`<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg"><rect width="${w}" height="${h}" rx="80" fill="white"/></svg>`;
   const crop=new Resvg(svg).render().asPng();
   const color=await sharp(path.join(wdir,input)).resize(w,h).composite([{input:gold}]).png().toBuffer();
   await sharp(color).composite([{input:crop,blend:'dest-in'}]).png().toFile(path.join(shots,name));
   await sharp(path.join(wdir,input)).resize(w,h).composite([{input:crop,blend:'dest-in'}]).png().toFile(path.join(shots,side+'-仅彩印.png'));
 }
 console.log('Previews rebuilt using the final native Gerber copper/mask intersection');
})().catch(e=>{console.error(e);process.exit(1)});
