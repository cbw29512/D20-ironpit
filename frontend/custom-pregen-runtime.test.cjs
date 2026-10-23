"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
require("./browser-test-runtime.cjs").loadWebsite();
const runtime=require("./custom-pregen-runtime.js");
const library=require("./custom-combatant-library.js");
function source(edition,cl="fighter",level=5) {
  return {id:"my-hero-"+cl,name:"Custom "+cl,kind:"character",ruleset:edition,
    class_id:cl,level,build_mode:"canonical_raw_snapshot"};
}
for(const edition of ["2014","2024"]) for(const cl of ["fighter","wizard"]) {
  const original=Object.values(window.IRON_PIT_BROWSER_HEROES).find(x=>x.ruleset===edition && x.class_id===cl && x.level===5);
  assert.ok(original,edition+" "+cl+" level 5 RAW build exists");
  const draft=source(edition,cl),card=runtime.decorate(draft);
  assert.equal(card.coverage_status,"custom_ready");
  assert.equal(card.compiled_template.name,draft.name);
  assert.equal(card.compiled_template.armor_class,original.armor_class);
  assert.equal(card.compiled_template.max_hp,original.max_hp);
  assert.deepEqual(card.compiled_template.attacks,original.attacks);
  assert.deepEqual(card.compiled_template.ability_scores,original.ability_scores);
  assert.deepEqual(card.compiled_template.spell_attack_actions,original.spell_attack_actions);
  const monster=edition==="2014"?"2014-goblin":"srd-goblin-warrior";
  const selection={ruleset:edition,hero_ids:[card.runnable_template_id],monster_ids:[monster],
    compiled_heroes:{[card.runnable_template_id]:card.compiled_template}};
  const battle=window.IRON_PIT_BROWSER_ENGINE.runEncounter(selection);
  assert.ok(battle.events.length>0,edition+" "+cl+" plays a full fight");
  assert.ok(["heroes_win","monsters_win","draw"].includes(battle.outcome));
  assert.equal(battle.setup.heroes[0].state.template.name,draft.name);
  assert.equal(battle.setup.heroes[0].state.template.max_hp,original.max_hp);
  assert.equal(battle.setup.heroes[0].state.template.class_id,cl);
  assert.equal(draft.build_mode,"canonical_raw_snapshot");
  for(const mutation of [
    template=>template.max_hp+=100,
    template=>template.attacks[0].bonus+=5,
    template=>template.level++,
    template=>template.ability_scores && (template.ability_scores.strength=30)
  ]) {
    const altered=structuredClone(card.compiled_template);mutation(altered);
    assert.throws(()=>window.IRON_PIT_BROWSER_ENGINE.runEncounter({...selection,compiled_heroes:{[card.runnable_template_id]:altered}}),/Custom pregen/);
  }
}
assert.equal(runtime.decorate({...source("2014"),attacks:[{damage:999}]}).coverage_status,"custom_draft");
assert.equal(runtime.decorate({...source("2014"),build_mode:"arbitrary"}).coverage_status,"custom_draft");
assert.equal(runtime.decorate(source("2014","artificer")).coverage_status,"custom_draft");
assert.equal(runtime.decorate(source("2024","fighter",21)).coverage_status,"custom_draft");
const backing=new Map();
global.localStorage={getItem:key=>backing.get(key)||null,setItem:(key,val)=>backing.set(key,val)};
library.save(source("2014"));
const nodes=new Map();
function fakeNode() {return {value:"",disabled:false,hidden:false,selected:false,children:[],listeners:{},style:{},
  classList:{add(){},remove(){}},dataset:{},
  append(...items){this.children.push(...items);if(!this.value&&items[0]?.value)this.value=items[0].value;},
  replaceChildren(...items){this.children=[...items];this.value=items.find(it=>it.selected)?.value||items[0]?.value||"";},
  addEventListener(name,fn){this.listeners[name]=fn;},showModal(){this.open=true;},
  close(){this.open=false;this.listeners.close?.();},
  setAttribute(){},removeAttribute(){},get options(){return this.children;}
};}
global.document={
  getElementById(id){if(!nodes.has(id))nodes.set(id,fakeNode());return nodes.get(id);},
  createElement(){return fakeNode();}
};
window.IRON_PIT_ENCOUNTER_PICKER={
  classOptions:()=>[{id:"fighter",name:"Fighter"}],LEVELS:[1,5],
  heroBuilds:()=>[],preferredHero:()=>null,sortedMonsters:()=>[],challengeRatings:()=>[]
};
vm.runInThisContext(fs.readFileSync(path.join(__dirname,"battlefield-picker.js"),"utf8"),{filename:"battlefield-picker.js"});
const picker=window.IRON_PIT_BATTLEFIELD_PICKER;
const state={ruleset:"2014",catalog:{heroes:[{id:"hero-fighter",name:"Fighter",class_id:"fighter",class_name:"Fighter",level:5,kind:"character",ruleset:"2014",coverage_status:"raw_ready",runnable_template_id:Object.values(window.IRON_PIT_BROWSER_HEROES).find(h=>h.ruleset==="2014"&&h.class_id==="fighter"&&h.level===5).id}],monsters:[]},
  heroSlots:Array(6).fill(null),monsterSlots:Array(6).fill(null)};
picker.bind(()=>state);
let selected=null;
picker.open(state,"heroes",0,(_side,_index,card)=>{selected=card;},()=>{});
const classes=nodes.get("picker-class");
classes.value="custom";classes.onchange();
assert.equal(nodes.get("confirm-card").disabled,false,"RAW custom pregen must be selectable");
nodes.get("confirm-card").listeners.click();
assert.equal(selected.coverage_status,"custom_ready");
assert.equal(selected.compiled_template.class_id,"fighter");
for(const page of ["index.html","../index.html"]) {
  const html=fs.readFileSync(path.join(__dirname,page),"utf8");
  assert.ok(html.includes('src="custom-pregen-runtime.js"'));
  assert.ok(html.indexOf('src="custom-pregen-runtime.js"')<html.indexOf('src="battlefield-picker.js"'));
}
console.log("RAW custom pregen selector and real 2014/2024 fighter/wizard fights passed.");
