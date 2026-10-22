const p=await eda.dmt_Project.getCurrentProjectInfo();
const pcb=p.data.find(i=>i.pcb).pcb;
const tab=await eda.dmt_EditorControl.openDocument(pcb.uuid);
await eda.dmt_EditorControl.activateDocument(tab);
const region=await eda.dmt_EditorControl.zoomToRegion(0,2362.2047,0,-3937.0079,tab);
await new Promise(r=>setTimeout(r,3000));
const f=await eda.dmt_EditorControl.getCurrentRenderedAreaImage(tab);
return {project:p.friendlyName,tab,region,imageSize:f?.size,sourceSize:(await eda.pcb_PrimitiveImage.getAllPrimitiveId()).length};
