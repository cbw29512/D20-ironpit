"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-armor-corrosion.js"), "utf8"));
const C = window.IRON_PIT_BROWSER_ARMOR_CORROSION;
const target = {armor_corrosion_penalties: {}, destroyed_armor_ids: []};
assert.deepEqual(C.afterHit(target,"chain",{hit:false,nonmagicalMetalArmor:true,itemBaseAC:16}),
  {penalty:0,destroyed:false,applied:false});
assert.deepEqual(C.afterHit(target,"chain",{hit:true,nonmagicalMetalArmor:false,itemBaseAC:16}),
  {penalty:0,destroyed:false,applied:false});
for (let i=1;i<=6;i++) {
  const r = C.afterHit(target,"chain",{hit:true,nonmagicalMetalArmor:true,itemBaseAC:16});
  assert.equal(r.penalty,-i);
  assert.equal(r.destroyed,i===6);
}
assert.equal(target.armor_corrosion_penalties.chain,6);
assert.deepEqual(target.destroyed_armor_ids,["chain"]);
assert.equal(C.afterHit(target,"chain",{hit:true,nonmagicalMetalArmor:true,itemBaseAC:16}).applied,false);
assert.equal(C.afterHit(target,"plate",{hit:true,nonmagicalMetalArmor:true,itemBaseAC:18}).penalty,-1);
assert.throws(()=>C.afterHit(target,"",{hit:true,nonmagicalMetalArmor:true,itemBaseAC:16}),/stable item ID/);
assert.equal(C.afterHit({armor_corrosion_penalties:{},destroyed_armor_ids:[]},
  "chain",{hit:true,nonmagicalMetalArmor:true,itemBaseAC:16}).penalty,-1);
console.log("Universal armor-item corrosion parity passed.");
