const fs=require('fs'), path=require('path');
const sharp=require('sharp');
const {Resvg}=require('@resvg/resvg-js');
const opentype=require('opentype.js');
const potrace=require('potrace');
const svgpath=require('svgpath');
const TARGET='D:/Users/zhangyue/Desktop/project/PCB-Art/ChatGPT-PCB-Art';
const gen='C:/Users/zhangyue/.codex/generated_images/01a13491-0e20-72d3-be0c-5db04bbec12c';
const ASSET=path.join(TARGET,'使用的文件'),WORK=path.join(TARGET,'.tmp-work'),SHOT=path.join(TARGET,'截图');
for(const p of [TARGET,ASSET,WORK,SHOT])fs.mkdirSync(p,{recursive:true});
const specs=[
 ['Q版龙娘',path.join(gen,'exec-564a83c5-589c-41f1-a16e-df6d002c4f97.png'),'ChatGPT_chibi_4K.png'],
 ['顶面右侧主图',path.join(gen,'exec-0f620482-ab77-4602-8ced-cdfa301a8e5b.png'),'ChatGPT_front_4K.jpg'],
 ['底面上中身',path.join(gen,'exec-45c8b045-8f86-4782-b5e5-c2dac914562b.png'),'ChatGPT_back_4K.jpg']
];
const fontBytes=fs.readFileSync('C:/Windows/Fonts/seguisb.ttf');
const font=opentype.parse(fontBytes.buffer.slice(fontBytes.byteOffset,fontBytes.byteOffset+fontBytes.byteLength));
function svg(body,w,h,pw,ph){return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${pw}" height="${ph}" viewBox="0 0 ${w} ${h}">${body}</svg>`;}
function uri(p){const ext=path.extname(p);return 'data:image/'+(ext==='.jpg'?'jpeg':'png')+';base64,'+fs.readFileSync(p).toString('base64');}
function png(svgstr){return new Resvg(svgstr,{font:{loadSystemFonts:false}}).render().asPng();}
function save(name,data){const p=path.join(WORK,name);fs.writeFileSync(p,data);return p;}
function trace(buffer){return new Promise((resolve,reject)=>potrace.trace(buffer,{threshold:128,blackOnWhite:true,turdSize:25,optCurve:true,optTolerance:.35,alphaMax:1},(err,s)=>err?reject(err):resolve(s)));}

function flatten(svgstr, w,h,side){
 const out=[];let points=0;
 for(const match of svgstr.matchAll(/<path\b[^>]*\bd="([^"]+)"/g)){
  const p=svgpath(match[1]).unshort().unarc().abs();let poly=[],x=0,y=0;
  function board(a,b){let bx,by;if(side==='front'){bx=60-b/20;by=a/20;}else{bx=a/20;by=b/20;}return [+(bx/.0254).toFixed(5),+(-by/.0254).toFixed(5)];}
  function append(a,b){const v=board(a,b);if(poly.length<2)poly.push(...v,'L');else poly.push(...v);points++;}
  function end(){if(poly.length>8){const last=poly.slice(-2);if(last[0]!==poly[0]||last[1]!==poly[1])poly.push(poly[0],poly[1]);out.push(poly);}poly=[];}
  p.iterate(seg=>{
   const c=seg[0];
   if(c==='M'){end();x=seg[1];y=seg[2];append(x,y);}
   else if(c==='L'){x=seg[1];y=seg[2];append(x,y);}
   else if(c==='C'){
    const [a,b,cx,cy,ex,ey]=seg.slice(1),sx=x,sy=y;
    const length=Math.hypot(a-sx,b-sy)+Math.hypot(cx-a,cy-b)+Math.hypot(ex-cx,ey-cy);
    const steps=Math.max(2,Math.min(300,Math.ceil(length/1.5)));
    for(let n=1;n<=steps;n++){const t=n/steps,u=1-t;append(u*u*u*sx+3*u*u*t*a+3*u*t*t*cx+t*t*t*ex,u*u*u*sy+3*u*u*t*b+3*u*t*t*cy+t*t*t*ey);}
    x=ex;y=ey;
   }else if(c==='Q')throw Error('Unexpected Q segment');else if(c==='Z')end();
  });end();
 }
 // Potrace emits even-odd contours with the same winding. The EDA image importer
 // uses winding to distinguish holes: reverse each odd containment-depth loop.
 const loops=out.map(p=>{const nums=p.filter(v=>typeof v==='number'),xy=[];for(let i=0;i<nums.length;i+=2)xy.push([nums[i],nums[i+1]]);let area=0;for(let i=0;i<xy.length-1;i++)area+=xy[i][0]*xy[i+1][1]-xy[i+1][0]*xy[i][1];return {xy,area:Math.abs(area),x0:Math.min(...xy.map(v=>v[0])),x1:Math.max(...xy.map(v=>v[0])),y0:Math.min(...xy.map(v=>v[1])),y1:Math.max(...xy.map(v=>v[1]))};});
 function inside(x,y,xy){let yes=false;for(let i=0,j=xy.length-1;i<xy.length;j=i++){const a=xy[i],b=xy[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;}
 for(const loop of loops){const [x,y]=loop.xy[0];const depth=loops.filter(o=>o!==loop&&o.area>loop.area&&x>=o.x0&&x<=o.x1&&y>=o.y0&&y<=o.y1&&inside(x,y,o.xy)).length;if(depth%2)loop.xy.reverse();}
 const fixed=loops.map(o=>[...o.xy[0],'L',...o.xy.slice(1).flat()]);
 return {paths:fixed,points};
}

(async()=>{
 const manifest=[];
 for(const [label,src,name]of specs){
  const m=await sharp(src).metadata();const dest=path.join(ASSET,name);
  fs.copyFileSync(src,path.join(ASSET,name.replace('_4K', '_AI原生').replace('.jpg','.png')));
  let p=sharp(src).resize({width:4096,height:4096,fit:'inside',kernel:'lanczos3'});
  if(name.endsWith('.jpg'))p=p.flatten({background:'#ffffff'}).jpeg({quality:96,chromaSubsampling:'4:4:4'});else p=p.png({compressionLevel:9});
  await p.toFile(dest);const mm=await sharp(dest).metadata();manifest.push({label,file:name,sourcePixels:[m.width,m.height],productionPixels:[mm.width,mm.height],method:'AI重绘后以Lanczos3重采样导出4096px长边；不标称原生4K'});
 }
 fs.writeFileSync(path.join(ASSET,'图像分辨率说明.json'),JSON.stringify(manifest,null,2));
 const frontImage=uri(path.join(ASSET,'ChatGPT_front_4K.jpg')),chibi=uri(path.join(ASSET,'ChatGPT_chibi_4K.png')),back=uri(path.join(ASSET,'ChatGPT_back_4K.jpg'));
 const main=`<image xlink:href="${frontImage}" x="0" y="0" width="100" height="60" preserveAspectRatio="xMidYMid slice"/>`;
 const q=`<image xlink:href="${chibi}" x="-4" y="29" width="36" height="36"/>`;
 const frontbody='<rect width="100" height="60" fill="white"/>'+main+q;
 const backbody='<rect width="60" height="100" fill="white"/>'+`<image xlink:href="${back}" x="1.4" y="2.4" width="57.2" height="95.3333" preserveAspectRatio="xMidYMin meet"/>`;
 save('front-color-landscape.png',png(svg(frontbody,100,60,4096,2458)));
 save('back-color-portrait.png',png(svg(backbody,60,100,2458,4096)));
 // Editable fabrication texture assets: each main image remains separate from the chibi object.
 const topMain=png(svg('<rect width="60" height="100" fill="white"/>'+`<g transform="translate(60 0) rotate(90)">${main}</g>`,60,100,2458,4096));
 const topQ=await sharp(path.join(ASSET,'ChatGPT_chibi_4K.png')).rotate(90).png().toBuffer();
 fs.writeFileSync(path.join(ASSET,'顶面主图_板面坐标_4K.jpg'),await sharp(topMain).jpeg({quality:96,chromaSubsampling:'4:4:4'}).toBuffer());
 fs.writeFileSync(path.join(ASSET,'顶面Q版_板面坐标_4K.png'),topQ);
 fs.writeFileSync(path.join(ASSET,'底面主图_完整板面_4K.jpg'),await sharp(png(svg(backbody,60,100,2458,4096))).jpeg({quality:96,chromaSubsampling:'4:4:4'}).toBuffer());

 // Convert the remastered image linework into fabrication geometry. A 20 px/mm raster
 // is an intermediate sampling grid, separate from the 4K color production assets.
 const quote1=font.getPath("I've got",5.2,13.8,6.7).toPathData(4);
 const quote2=font.getPath('you',5.2,24,9.1).toPathData(4);
 const quote=`<path d="${quote1}"/><path d="${quote2}"/>`;
 const frontDecor=`<path d="M3 10 V3 H26 M94 3 H97 V11 M97 51 V57 H86" fill="none" stroke="black" stroke-width="0.22" stroke-linecap="round"/><path d="M36 8 L36.7 10.3 L39 11 L36.7 11.7 L36 14 L35.3 11.7 L33 11 L35.3 10.3 Z"/>`;
 // Reuse the actual original project flourish, including its interior holes.
 const originalFlourish=fs.readFileSync(path.join(__dirname,'../analysis/vector_L1_7ce2c67c87592456.svg'),'utf8');
 const flourishPath=originalFlourish.match(/<path\b[^>]*\bd="([^"]+)"/)[1];
 const leftFlourish=`<svg x="2.5" y="2.5" width="7.5" height="7.5" viewBox="-483.4545 -452 1506.4545 1507"><path d="${flourishPath}" fill-rule="nonzero"/></svg>`;
 const backDecor=leftFlourish+`<g transform="translate(60 0) scale(-1 1)">${leftFlourish}</g><path d="M3 89 V97 H13 M47 97 H57 V89" fill="none" stroke="black" stroke-width="0.2" stroke-linecap="round"/>`;
 const starSpecs=[[43.5,12,0.72],[49.1,12,0.48],[45.75,17.4,0.6],[55.5,16,0.55],[56,9.4,0.5],[89.1,6.45,0.55],[84.25,12.4,0.7],[89.45,10,0.85],[92.3,23,0.55]];
 const starDecor=starSpecs.map(([x,y,r])=>`<path d="M${x} ${y-r} L${x+r*.24} ${y-r*.24} L${x+r} ${y} L${x+r*.24} ${y+r*.24} L${x} ${y+r} L${x-r*.24} ${y+r*.24} L${x-r} ${y} L${x-r*.24} ${y-r*.24} Z"/>`).join('');
 // Follow the existing pale halo, breaking the metallic highlights into flowing
 // ribbons. Width varies smoothly; the 0.14 mm end width avoids needle tips.
 const haloSpecs=[
  [23.8,-169,-150,.25],[23.8,-147,-137,.21],[23.8,-128,-122,.24],
  [23.8,-74,-58,.24],[23.8,-54,-36,.27],[23.8,-31,-18,.23],[23.8,-12,-6,.21],
  [24.55,-160,-150,.18],[23.05,-146,-139,.18],
  [24.55,-66,-53,.19],[23.05,-28,-21,.18]
 ];
 function haloRibbon([radius,a0,a1,maxWidth]){
   const edges=[[],[]],n=Math.ceil((a1-a0)*3);
   for(let i=0;i<=n;i++){
     const t=i/n,a=(a0+(a1-a0)*t)*Math.PI/180;
     const r=radius+.065*Math.sin(Math.PI*t)*Math.sin(2*Math.PI*t);
     const width=.14+(maxWidth-.14)*Math.pow(Math.sin(Math.PI*t),.8);
     for(let side=0;side<2;side++){
       const rr=r+(side===0?1:-1)*width/2;
       edges[side].push([71.5+rr*Math.cos(a),27.3+rr*Math.sin(a)]);
     }
   }
   const pts=edges[0].concat(edges[1].reverse());
   return `<path d="M${pts.map(p=>p.map(v=>v.toFixed(4)).join(' ')).join(' L')} Z"/>`;
 }
 const haloDecor=haloSpecs.map(haloRibbon).join('');
 fs.writeFileSync(path.join(ASSET,'顶面光晕_断续沉金高光.svg'),svg(haloDecor,100,60,2000,1200));
 save('front-halo-white.png',png(svg('<rect width="100" height="60" fill="black"/><g fill="white">'+haloDecor+'</g>',100,60,2000,1200)));
 fs.writeFileSync(path.join(ASSET,'顶面星光_沉金.svg'),svg(starDecor,100,60,2000,1200));
 fs.writeFileSync(path.join(ASSET,'底面原工程角花_沉金.svg'),svg(backDecor,60,100,1200,2000));
 fs.writeFileSync(path.join(ASSET,'Ive_got_you_金属文字.svg'),svg(quote+frontDecor,100,60,2000,1200));
 const frontColor=png(svg(frontbody,100,60,2000,1200)),backColor=png(svg(backbody,60,100,1200,2000));
 async function linesFrom(buffer){
   return await sharp(buffer).flatten({background:'white'}).greyscale().threshold(156).negate().dilate(1).toBuffer();
 }
 let fLines=await linesFrom(frontColor),bLines=await linesFrom(backColor);
 // Remove the chibi from decorative copper; it stays fully in the color silk object.
 const excludeChibi=png(svg('<rect width="100" height="60" fill="white"/><rect x="0" y="28.5" width="32.5" height="31.5" fill="black"/>',100,60,2000,1200));
 fLines=await sharp(fLines).composite([{input:excludeChibi,blend:'multiply'}]).png().toBuffer();
 const fSelection=png(svg('<rect width="100" height="60" fill="black"/><ellipse cx="73.8" cy="14" rx="4.5" ry="5" fill="white"/><ellipse cx="58.7" cy="44.5" rx="3.8" ry="4" fill="white"/><ellipse cx="76" cy="47.5" rx="3.8" ry="4.5" fill="white"/><ellipse cx="65.7" cy="17.5" rx="4.9" ry="4.9" fill="black"/>',100,60,2000,1200));
 let fOpen=await sharp(fLines).composite([{input:fSelection,blend:'multiply'}]).png().toBuffer();
 const bSelection=png(svg('<rect width="60" height="100" fill="white"/><ellipse cx="23" cy="24" rx="9.3" ry="10" fill="black"/><ellipse cx="53" cy="27" rx="7.1" ry="7.5" fill="black"/><ellipse cx="50" cy="40" rx="10.7" ry="7.6" fill="black"/><ellipse cx="14" cy="41" rx="7" ry="10" fill="black"/>',60,100,1200,2000));
 let bOpen=await sharp(bLines).composite([{input:bSelection,blend:'multiply'}]).png().toBuffer();
 // Open only the spirit outline and its motion trails; keep its blue eyes in silk.
 const spiritSelect=png(svg('<rect width="60" height="100" fill="black"/><ellipse cx="53.5" cy="27.7" rx="4.8" ry="4.8" fill="white"/><ellipse cx="53.4" cy="27.2" rx="2.7" ry="2.4" fill="black"/><path d="M46.3 29 H49.1 V35.2 H46.3 Z" fill="white"/>',60,100,1200,2000));
 const spiritOutline=await sharp(bLines).composite([{input:spiritSelect,blend:'multiply'}]).png().toBuffer();
 bOpen=await sharp(bOpen).composite([{input:spiritOutline,blend:'lighten'}]).png().toBuffer();
 const spiritGlints=[[58.1,21.5,.65],[47.2,23.3,.45]].map(([x,y,r])=>`<path d="M${x} ${y-r} L${x+r*.25} ${y-r*.25} L${x+r} ${y} L${x+r*.25} ${y+r*.25} L${x} ${y+r} L${x-r*.25} ${y+r*.25} L${x-r} ${y} L${x-r*.25} ${y-r*.25} Z"/>`).join('');
 async function addGraphics(line,body,w,h,pw,ph){const dec=png(svg('<rect width="'+w+'" height="'+h+'" fill="black"/><g fill="white">'+body.replaceAll('stroke="black"','stroke="white"')+'</g>',w,h,pw,ph));return sharp(line).composite([{input:dec,blend:'lighten'}]).png().toBuffer();}
 fLines=await addGraphics(fLines,quote+frontDecor+starDecor+haloDecor,100,60,2000,1200);fOpen=await addGraphics(fOpen,quote+frontDecor+starDecor+haloDecor,100,60,2000,1200);
 bLines=await addGraphics(bLines,backDecor+spiritGlints,60,100,1200,2000);bOpen=await addGraphics(bOpen,backDecor+spiritGlints,60,100,1200,2000);
 fs.writeFileSync(path.join(ASSET,'底面精灵星光_沉金.svg'),svg(spiritGlints,60,100,1200,2000));
 const frontSafe=png(svg('<rect width="100" height="60" fill="black"/><rect x="0.5" y="0.5" width="99" height="59" rx="3.5" fill="white"/>',100,60,2000,1200));
 const backSafe=png(svg('<rect width="60" height="100" fill="black"/><rect x="0.5" y="0.5" width="59" height="99" rx="3.5" fill="white"/>',60,100,1200,2000));
 async function safe(buf,m){return sharp(buf).composite([{input:m,blend:'multiply'}]).png().toBuffer();}
 fLines=await safe(fLines,frontSafe);fOpen=await safe(fOpen,frontSafe);bLines=await safe(bLines,backSafe);bOpen=await safe(bOpen,backSafe);
 const layerSpec={};
 for(const [name,buf,w,h,side]of [['front-copper',fLines,2000,1200,'front'],['front-open',fOpen,2000,1200,'front'],['back-copper',bLines,1200,2000,'back'],['back-open',bOpen,1200,2000,'back']]){
   save(name+'-white.png',buf);
   const binary=await sharp(buf).flatten({background:'black'}).greyscale().threshold(128).negate().png().toBuffer();
   const vector=await trace(binary);save(name+'.svg',vector);
   const f=flatten(vector,w,h,side);layerSpec[name]={paths:f.paths,points:f.points,contours:f.paths.length};
   console.log(name,'contours',f.paths.length,'points',f.points);
 }
 fs.writeFileSync(path.join(WORK,'fabrication-paths.json'),JSON.stringify(layerSpec));
 const gold='#c29b42';
 async function overlay(color,mask,w,h,out){const m=await sharp(mask).resize(w,h).greyscale().threshold(128).raw().toBuffer();const c=await sharp({create:{width:w,height:h,channels:3,background:gold}}).joinChannel(m,{raw:{width:w,height:h,channels:1}}).png().toBuffer();await sharp(color).resize(w,h).composite([{input:c}]).png().toFile(path.join(SHOT,out));}
 await overlay(frontColor,fOpen,2000,1200,'预览-顶面-双图与金属文字.png');
 await overlay(backColor,bOpen,1200,2000,'预览-底面-上中身与金属描边.png');
 fs.writeFileSync(path.join(WORK,'layout.json'),JSON.stringify({board:{widthMm:60,heightMm:100,cornerRadiusMm:4},front:{viewWidthMm:100,viewHeightMm:60,chibiRect:[-4,29,36,36],quote:"I've got you",quoteLines:["I've got","you"],goldStars:starSpecs,goldHalo:{centerMm:[71.5,27.3],ribbons:haloSpecs,minDesignedWidthMm:.14,description:'11段断续曲线，沿彩印光晕，主弧与短伴随弧长短错落；宽度为制作设计值，非板厂能力认证'}},back:{imageRect:[1.4,2.4,57.2,95.3333],croppedTo:'上中身，保留向右伸出的手与浮游精灵',topFlourishes:{source:'DeepSeek IMAGE 7ce2c67c87592456',sizeMm:7.5,positionsMm:[[2.5,2.5],[50,2.5]],mirroredPair:true},spiritFinish:{colorSilk:'blue-white body and blue eyes retained',enig:'outer contour, partial motion trails, 2 nearby glints'}},maskRasterPxPerMm:20,traceThreshold:156,traceMinComponentPixels:25},null,2));
 console.log('Prepared',TARGET);
})().catch(e=>{console.error(e);process.exit(1)});
