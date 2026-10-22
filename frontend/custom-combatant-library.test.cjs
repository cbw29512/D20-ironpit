const test = require("node:test");
const assert = require("node:assert/strict");
const records = new Map();
global.localStorage = {getItem: key => records.get(key) ?? null, setItem: (key,val) => records.set(key,val)};
const lib = require("./custom-combatant-library.js");
test("custom monster save is namespaced and survives a library reload", () => {
  const stored = lib.save({id:"test-dummy",name:"Test Dummy",kind:"monster",ruleset:"2014",armor_class:0});
  assert.equal(stored.custom,true);
  assert.equal(stored.runnable_template_id,null);
  assert.equal(lib.list("monster","2014")[0].armor_class,0);
  assert.equal(lib.list("character","2014").length,0);
});
test("same ID may exist for distinct editions and kinds; saving again replaces only matching card", () => {
  lib.save({id:"test-dummy",name:"Hero",kind:"character",ruleset:"2014"});
  lib.save({id:"test-dummy",name:"Other Edition",kind:"monster",ruleset:"2024"});
  lib.save({id:"test-dummy",name:"Renamed Dummy",kind:"monster",ruleset:"2014"});
  assert.equal(lib.list("monster","2014").length,1);
  assert.equal(lib.list("monster","2014")[0].name,"Renamed Dummy");
  assert.equal(lib.list("monster","2024").length,1);
  assert.equal(lib.list("character","2014").length,1);
});
test("invalid custom combatants are rejected", () => {
  assert.throws(()=>lib.save({kind:"monster",ruleset:"2014",id:"Bad ID"}),/Invalid custom combatant/);
});
