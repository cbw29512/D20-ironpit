"use strict";
const fs = require("node:fs"), path = require("node:path");
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
require("./browser-catalog.js");require("./battle-lab.js");require("./browser-turbo.js");

function labels(card) {
  const found = new Set();
  for (const attack of card.attacks || []) {
    if (attack.attack_kind) found.add("attack:" + attack.attack_kind);
    if (attack.damage_type) found.add("damage:" + attack.damage_type);
    for (const effect of attack.effects || []) {
      if (effect.kind) found.add("effect:" + effect.kind);
      if (effect.damage_type) found.add("damage:" + effect.damage_type);
    }
  }
  for (const trait of card.traits || []) found.add("trait:" + trait);
  for (const action of card.saving_throw_actions || []) found.add("save:" + (action.id || action.name));
  if (card.attack_action) found.add("multiattack");
  for (const id of Object.keys(card.resources || {})) found.add("resource:" + id);
  return [...found];
}
(async()=>{
  const cases=[], summary={};
  for (const edition of ["2014","2024"]) {
    const catalog=await IRON_PIT_BROWSER_CATALOG.buildCatalog(edition);
    const heroes=catalog.heroes.filter(c=>c.coverage_status==="raw_ready"&&c.runnable_template_id);
    const monsters=catalog.monsters.filter(c=>c.coverage_status==="raw_ready"&&c.runnable_template_id);
    assert.ok(heroes.length&&monsters.length,edition+" certified rosters required");
    const heroRuntime=IRON_PIT_BROWSER_HEROES;
    const monsterRuntime=edition==="2014"?IRON_PIT_BROWSER_MONSTERS_2014:IRON_PIT_BROWSER_MONSTERS;
    const candidates=monsters.map(c=>({card:c,mechanics:labels(monsterRuntime[c.runnable_template_id]||{})}));
    const covered=new Set(), selected=[];
    while(candidates.length&&selected.length<50){
      candidates.sort((a,b)=>b.mechanics.filter(m=>!covered.has(m)).length-a.mechanics.filter(m=>!covered.has(m)).length||a.card.id.localeCompare(b.card.id));
      const next=candidates.shift();
      if(selected.length&&!next.mechanics.some(m=>!covered.has(m)))break;
      selected.push(next);next.mechanics.forEach(m=>covered.add(m));
    }
    for(let i=0;i<selected.length;i++){
      const selectedMonster=selected[i],hero=heroes[i%heroes.length];
      const selection={ruleset:edition,hero_ids:[hero.runnable_template_id],monster_ids:[selectedMonster.card.runnable_template_id]};
      const seed=27001+i, before=JSON.stringify([heroRuntime[hero.runnable_template_id],monsterRuntime[selectedMonster.card.runnable_template_id]]);
      try{
        const battle=IRON_PIT_BROWSER_TURBO.runSeeded(selection,seed).battle;
        assert.ok(["heroes_win","monsters_win","draw"].includes(battle.outcome));
        assert.ok(battle.events.length>0);
        assert.equal(JSON.stringify([heroRuntime[hero.runnable_template_id],monsterRuntime[selectedMonster.card.runnable_template_id]]),before,"cards mutated");
        cases.push({edition,hero:hero.runnable_template_id,monster:selectedMonster.card.runnable_template_id,seed,
          declared:selectedMonster.mechanics,outcome:battle.outcome,rounds:battle.rounds,events:battle.events.length,
          observed_features:[...new Set(battle.events.map(e=>e.feature_id).filter(Boolean))].sort(),
          observed_conditions:[...new Set(battle.events.flatMap(e=>e.applied_condition_ids||[]))].sort(),
          status:"PASS"});
      }catch(error){cases.push({edition,hero:hero.runnable_template_id,monster:selectedMonster.card.runnable_template_id,seed,declared:selectedMonster.mechanics,status:"FAIL",error:String(error)});}
    }
    summary[edition]={selected_fights:selected.length,declared_mechanic_labels:covered.size};
  }
  const report={schema_version:1,scope:"generated monster diversity probes; observed events do not certify RAW",summary,total:cases.length,passed:cases.filter(c=>c.status==="PASS").length,failed:cases.filter(c=>c.status==="FAIL").length,cases};
  if(process.env.IRON_PIT_GENERATED_RESULTS_PATH){const dest=process.env.IRON_PIT_GENERATED_RESULTS_PATH;fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,JSON.stringify(report,null,2)+"\n");}
  console.log(JSON.stringify({summary,total:report.total,passed:report.passed,failed:report.failed}));
  assert.equal(report.failed,0,"generated fights must complete without errors or card mutations");
})().catch(e=>{console.error(e);process.exitCode=1});
