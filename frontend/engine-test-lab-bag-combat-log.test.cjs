"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

(async () => {
  try {
    require("./browser-test-runtime.cjs").loadWebsite();
    const load = name => vm.runInThisContext(
      fs.readFileSync(path.join(__dirname, name), "utf8"), {filename: name},
    );
    for (const name of [
      "custom-monster-runtime.js", "battle-lab.js", "browser-turbo.js",
      "engine-test-lab-punching-bag.js", "engine-test-lab-bag-fight.js",
      "battle-log-format.js", "battle-log-export.js",
      "engine-test-lab-bag-combat-log.js",
    ]) load(name);
    const fighter = Object.values(window.IRON_PIT_BROWSER_HEROES).find(
      x => x.ruleset === "2014" && x.class_id === "fighter" && x.level === 1);
    assert.ok(fighter, "A real source pregen must exist.");
    const entry = {kind:"punching_bag", edition:"2014",
      source_kind:"pregen", source_id:fighter.id};
    const originalHeroes = window.IRON_PIT_BROWSER_HEROES;
    const baseline = window.IRON_PIT_TEST_BAG_FIGHT.run(entry, 12345);
    const battle = baseline.replay.battle;
    const row = {edition:"2014", kind:"pregen",
      card_id:fighter.id, card_name:fighter.name,
      attempts:[{attempt:1, seed:12345,
        diagnostic_id:baseline.replay.diagnostic_id,
        event_count:battle.events.length, outcome:battle.outcome}]};
    const api = window.IRON_PIT_TEST_BAG_COMBAT_LOG;
    const output = api.replayCase(row,0);
    assert.equal(output.event_json.type,"iron_pit_combat_transcript");
    assert.equal(output.metadata.event_count,battle.events.length);
    assert.deepEqual(output.event_json.events,battle.events);
    assert.match(output.narrative,/ACTUAL COMBAT LOG/);
    assert.match(output.narrative,/Round 0/);
    assert.match(output.narrative,/Round 1/);
    assert.match(output.narrative,/d20|HIT|MISS/);
    assert.match(output.narrative,/HP [0-9]/);
    assert.match(output.narrative,/Punching Bag/);
    assert.strictEqual(window.IRON_PIT_BROWSER_HEROES,originalHeroes);
    assert.throws(() => api.replayCase({...row,attempts:[
      {...row.attempts[0],diagnostic_id:"wrong"}]},0),/Replay diagnostic differs/);
    assert.throws(() => api.replayCase(row,2),/does not exist/);

    // The browser UI must allow selecting ALL cases, not just the first 150
    // visible coverage table rows; it stores just the selected fight's events.
    const nodes = Object.fromEntries([
      "bag-card-select","bag-details","bag-attempt","bag-replay",
      "bag-combat-txt","bag-combat-json","bag-combat-message",
      "bag-combat-events",
    ].map(id=>[id, element()]));
    function element() {
      return {textContent:"",value:"",disabled:false,children:[],handlers:{},
        replaceChildren(...items){this.children=items;},
        append(item){this.children.push(item);},
        addEventListener(type,fn){this.handlers[type]=fn;}};
    }
    global.document = {
      getElementById:id=>nodes[id]||null,
      createElement:()=>element(),body:{append(){}},
    };
    load("engine-test-lab-bag-combat-view.js");
    const view = window.IRON_PIT_TEST_BAG_COMBAT_VIEW;
    view.install();
    view.setCases([row,{...row,card_id:"second-id",card_name:"Second"}]);
    assert.equal(nodes["bag-card-select"].children.length,2);
    assert.equal(nodes["bag-attempt"].children.length,1);
    assert.equal(nodes["bag-replay"].disabled,false);
    nodes["bag-replay"].handlers.click();
    assert.match(nodes["bag-combat-events"].textContent,/Round 1/);
    assert.equal(nodes["bag-combat-txt"].disabled,false);
    assert.equal(nodes["bag-combat-json"].disabled,false);
    nodes["bag-card-select"].value="1";
    nodes["bag-card-select"].handlers.change();
    assert.equal(nodes["bag-combat-txt"].disabled,true);
    assert.equal(nodes["bag-replay"].disabled,false);

    const html = fs.readFileSync(path.join(__dirname,"engine-test-lab.html"),"utf8");
    const scripts = [...html.matchAll(/<script defer src="([^"]+)"/g)]
      .map(match=>match[1]);
    for(const script of ["battle-log-format.js","battle-log-export.js",
      "engine-test-lab-bag-combat-log.js","engine-test-lab-bag-combat-view.js"]){
      assert.ok(scripts.includes(script),script+" missing from Test Workbench");
    }
    assert.ok(scripts.indexOf("battle-log-format.js")<
      scripts.indexOf("engine-test-lab-bag-combat-log.js"));
    for(const id of ["bag-card-select","bag-replay","bag-combat-txt",
      "bag-combat-json","bag-combat-events"]) assert.match(html,
      new RegExp('id="'+id+'"'));
    console.log("Source-seeded actual combat transcript, all-card selector, and raw events passed.");
  } catch (error) {
    console.error("Full combat transcript test failed",error);
    process.exitCode=1;
  }
})();