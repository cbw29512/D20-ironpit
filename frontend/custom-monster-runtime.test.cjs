"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
require("./browser-test-runtime.cjs").loadWebsite();
const {makeDefinition} = require("./combatant-builder.js");
const {compile,decorate} = require("./custom-monster-runtime.js");

function fields(ruleset) {
  return {
    id:"combat-dummy",name:"Combat Dummy",kind:"monster",ruleset,archetype:"training construct",size:"medium",
    challenge_rating:"1/4",armor_class:"0",max_hp:"50",speed_ft:"30",initiative_bonus:"0",
    attack_id:"claw",attack_name:"Claw",attack_kind:"melee",attack_bonus:"5",
    damage_count:"1",damage_size:"6",damage_bonus:"2",damage_type:"slashing",
    on_hit_effects:[
      {kind:"damage",damage_type:"fire",count:"1",size:"4",bonus:"0"},
      {kind:"prone"},
      {kind:"save_condition",save_ability:"constitution",dc:"11",condition:"poisoned",duration_rounds:"2"},
    ],
  };
}
for(const [edition,heroId] of [["2014","karnok-stoneward-2014-l1"],["2024","karnok-stoneward-l1"]]) {
  const source=makeDefinition(fields(edition));
  const before=JSON.stringify(source);
  const card=decorate({...source,custom:true,coverage_status:"custom_draft",runnable_template_id:null});
  assert.equal(card.coverage_status,"custom_ready",edition);
  assert.equal(card.compiled_template.armor_class,0);
  assert.equal(card.compiled_template.challenge_rating,"1/4");
  assert.equal(card.compiled_template.attacks[0].onHitDamage[0].damageType,"fire");
  assert.equal(card.compiled_template.attacks[0].proneMaxSize,"gargantuan");
  assert.equal(card.compiled_template.attacks[0].onHitConditionSave.conditionId,"poisoned");
  assert.equal(card.compiled_template.primary_attack_id,"claw");
  const selection={ruleset:edition,hero_ids:[heroId],monster_ids:[card.runnable_template_id],
    compiled_monsters:{[card.runnable_template_id]:card.compiled_template}};
  const fight=window.IRON_PIT_BROWSER_ENGINE.runEncounter(selection);
  assert.ok(fight.events.length>0,edition+" custom fight should resolve");
  assert.ok(["heroes_win","monsters_win","draw"].includes(fight.outcome),edition);
  assert.equal(fight.setup.monsters[0].state.template.armor_class,0);
  assert.equal(JSON.stringify(source),before,"fight must not mutate source custom card");
}
const invalid=makeDefinition(fields("2014"));
invalid.attacks[0].effects.reverse();
assert.equal(decorate(invalid).coverage_status,"custom_draft");
assert.match(decorate(invalid).compile_error,/effect/);
assert.throws(()=>compile({...makeDefinition(fields("2014")),unknown_innate_spell:"fireball"}),/unsupported field/);
assert.throws(()=>compile({...makeDefinition(fields("2014")),kind:"character"}),/unsupported schema/);
assert.throws(()=>compile({...makeDefinition(fields("2014")),challenge_rating:"100"}),/Challenge Rating/);
for(const page of ["index.html","../index.html"]) {
  const html=fs.readFileSync(path.join(__dirname,page),"utf8");
  assert.ok(html.includes('src="custom-monster-runtime.js"'));
  assert.ok(html.indexOf('src="custom-monster-runtime.js"')<html.indexOf('src="battlefield-picker.js"'));
}

const vm=require("node:vm");
const storage=new Map();
global.localStorage={getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value)};
const library=require("./custom-combatant-library.js");
library.save(makeDefinition(fields("2014")));
const elements=new Map();
function fakeNode() {
  return {value:"",selected:false,disabled:false,hidden:false,children:[],listeners:{},style:{},
    classList:{add(){},remove(){}},dataset:{},
    append(...items){this.children.push(...items);if(!this.value&&items[0]?.value)this.value=items[0].value;},
    replaceChildren(...items){this.children=[...items];this.value=items.find(item=>item.selected)?.value||items[0]?.value||"";},
    addEventListener(event,handler){this.listeners[event]=handler;},
    showModal(){this.open=true;},close(){this.open=false;this.listeners.close?.();},
    setAttribute(){},removeAttribute(){},
    get options(){return this.children;}
  };
}
global.document={
  getElementById(id){if(!elements.has(id))elements.set(id,fakeNode());return elements.get(id);},
  createElement(){return fakeNode();}
};
window.IRON_PIT_ENCOUNTER_PICKER={
  challengeRatings:()=>["0","1/4"],sortedMonsters:(cards)=>cards,
  classOptions:()=>[],LEVELS:[1],heroBuilds:()=>[],preferredHero:()=>null,
};
vm.runInThisContext(fs.readFileSync(path.join(__dirname,"battlefield-picker.js"),"utf8"),{filename:"battlefield-picker.js"});
const picker=window.IRON_PIT_BATTLEFIELD_PICKER;
const state={ruleset:"2014",catalog:{heroes:[],monsters:[]},
  heroSlots:Array(6).fill(null),monsterSlots:Array(6).fill(null)};
picker.bind(()=>state);
let picked=null;
picker.open(state,"monsters",0,(_side,_index,card)=>{picked=card;},()=>{});
const crSelect=elements.get("picker-cr");
crSelect.value="custom";crSelect.onchange();
assert.equal(elements.get("confirm-card").disabled,false,"saved supported monster must be selectable");
elements.get("confirm-card").listeners.click();
assert.equal(picked?.coverage_status,"custom_ready");
assert.equal(picked?.compiled_template.armor_class,0);

console.log("Saved custom monster homebrew browser runtime fights passed 2014 and 2024.");
