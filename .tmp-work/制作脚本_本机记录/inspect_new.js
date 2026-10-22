const project=await eda.dmt_Project.getCurrentProjectInfo();
const pcb=project.data.find(i=>i.itemType==='Board').pcb;
const tab=await eda.dmt_EditorControl.openDocument(pcb.uuid);
await new Promise(r=>setTimeout(r,1400));
await eda.dmt_EditorControl.zoomToAllPrimitives(tab);
return {name:project.friendlyName,uuid:project.uuid,pcbUuid:pcb.uuid,tab,
 copperLayers:await eda.pcb_Layer.getTheNumberOfCopperLayers(),
 vectorImages:await eda.pcb_PrimitiveImage.getAllPrimitiveId(),
 colorObjects:await eda.pcb_PrimitiveObject.getAllPrimitiveId(),
 pads:await eda.pcb_PrimitivePad.getAllPrimitiveId(),vias:await eda.pcb_PrimitiveVia.getAllPrimitiveId()};
