const tree=await eda.dmt_EditorControl.getSplitScreenTree();
const tab=tree.tabs.find(t=>t.data?.doctype===15);
if(!tab)throw new Error('No preview tab open');
const active=await eda.dmt_EditorControl.activateDocument(tab.tabId);
return {active,tabId:tab.tabId};
