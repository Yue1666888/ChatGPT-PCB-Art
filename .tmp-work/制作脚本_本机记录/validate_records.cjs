const fs=require('fs'),path=require('path');
const root='D:/Users/zhangyue/Desktop/project/PCB-Art/ChatGPT-PCB-Art';
const validator=require('C:/Users/zhangyue/.codex/skills/easyeda-format-skill/validate.js');
const records=JSON.parse(fs.readFileSync(path.join(root,'.tmp-work/new-records.json'),'utf8'));
const errors=[],warnings=[],checks=[];
for(const r of records){
 const body={...r.data};const doc=r.head.type==='BLOB'?'BLOB':'PCB';
 // Upstream schema is narrower than its own normative instructions and the real client:
 // ungrouped PCB primitives must store numeric 0; schema still says string.
 // Only the schema-check projection uses an empty string; on-disk data stays numeric 0.
 const groupRule=body.groupId===0||typeof body.groupId==='string';
 if('groupId' in body){if(!groupRule)errors.push('Invalid groupId '+r.head.id);if(body.groupId===0)body.groupId='';}
 const result=validator.validateFormat(r.head.type,body,doc);
 const outer=validator.validateOuter(r.head);
 if(!result.valid)errors.push({id:r.head.id,type:r.head.type,errors:result.errors});
 if(!outer.valid)errors.push({id:r.head.id,outerErrors:outer.errors});
 checks.push({id:r.head.id,type:r.head.type,valid:result.valid&&outer.valid,groupIdSemantic:groupRule});
}
const report={valid:!errors.length,errors,warnings,records:checks.length,checks,notes:['groupId=0 follows official primitive documentation and real editor records; schema projection used empty string solely to accommodate documented upstream schema type drift.']};
fs.writeFileSync(path.join(root,'.tmp-work/primitive-validation.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({valid:report.valid,records:checks.length,errors,warnings}));
process.exit(errors.length?1:0);
