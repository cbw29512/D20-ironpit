"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = name => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), {filename:name});

// Use production homebrew compiler, test bag builder and battlefield picker.
function item() {
  return {
    value:"", options:[], children:[], selected:false, disabled:false,
    style:{}, classList:{add(){},remove(){}}, hidden:false,
    replaceChildren(...children) {
      this.options = [...children];
      this.value = children[0]?.value || "";
    },
    append(...children) {
      const first = !this.options.length;
      this.options.push(...children);
      if (first) this.value = children[0]?.value || "";
    },
    addEventListener(name, callback) { this[name] = callback; },
    setAttribute() {}, removeAttribute() {}, showModal() {}, close() {},
  };
}
const ids = new Map();
global.document = {
  getElementById(id) {
    if (!ids.has(id)) ids.set(id, item());
    return ids.get(id);
  },
  createElement: () => item(),
};
const el = id => document.getElementById(id);
try {
  load("custom-monster-runtime.js");
  load("engine-test-lab-punching-bag.js");
  load("battlefield-bag-runner.js");
  load("encounter-picker.js");
  load("battlefield-picker.js");
  window.IRON_PIT_CUSTOM_LIBRARY = {list: () => []};
  const selected = [];
  const picker = window.IRON_PIT_BATTLEFIELD_PICKER;
  let state;
  picker.bind(() => state);
  for (const edition of ["2014","2024"]) {
    // Catalog represents the real source roster, not the extra test card.
    const official = [{
      id:"official-cr0",name:"Official CR Zero",challenge_rating:"0",
      kind:"monster",ruleset:edition,coverage_status:"raw_ready",
      runnable_template_id:"official-cr0",
    }];
    state = {ruleset:edition,catalog:{monsters:official,heroes:[]},
      heroSlots:Array(6).fill(null),monsterSlots:Array(6).fill(null)};
    picker.open(state,"monsters",0,(_side,_index,card)=>selected.push(card),()=>{});
    const cr = el("picker-cr"), choices = el("picker-monster");
    assert.ok(cr.options.some(o=>o.value==="0"),"CR 0 must be selectable.");
    cr.value = "0";
    cr.onchange();
    const bagOption = choices.options.find(o=>/Punching Bag/.test(o.textContent));
    assert.ok(bagOption,edition+" bag missing from CR 0");
    assert.match(bagOption.textContent,/TEST ONLY/);
    assert.ok(choices.options.some(o=>/Official CR Zero/.test(o.textContent)),
      "Training dummy must not replace official CR 0 monsters.");
    choices.value = bagOption.value;
    choices.onchange();
    assert.equal(el("confirm-card").disabled,false);
    assert.match(el("picker-note").textContent,/10,000 HP/);
    el("confirm-card").click();
    const card = selected.at(-1);
    assert.equal(card.ruleset,edition);
    assert.equal(card.challenge_rating,"0");
    assert.equal(card.custom,true);
    assert.equal(card.test_only,true);
    assert.equal(card.coverage_status,"custom_ready");
    assert.equal(card.compiled_template.id,card.runnable_template_id);
    assert.equal(card.compiled_template.max_hp,10000);
    assert.equal(card.compiled_template.armor_class,10);
    assert.equal(card.compiled_template.attacks[0].fixedDamage,0);
    assert.equal(card.compiled_template.saving_throw_bonuses.constitution,1);
    assert.equal(official.length,1,"Official catalog must remain unchanged.");
    assert.equal(state.catalog.monsters,official);
  }
  // A standalone custom-monster editor may not load the optional test runner.
  // Its normal CR picker must still function without hiding official monsters.
  const runner = window.IRON_PIT_BATTLEFIELD_BAG_RUNNER;
  delete window.IRON_PIT_BATTLEFIELD_BAG_RUNNER;
  picker.open(state,"monsters",0,()=>{},()=>{});
  el("picker-cr").value = "0";
  el("picker-cr").onchange();
  assert.ok(el("picker-monster").options.some(o => /Official CR Zero/.test(o.textContent)));
  assert.ok(el("picker-monster").options.every(o => !/Punching Bag/.test(o.textContent)));
  window.IRON_PIT_BATTLEFIELD_BAG_RUNNER = runner;
  console.log("CR 0 test-only Punching Bag selectable in both editions without roster mutation.");
} catch (error) {
  console.error("Player-facing Punching Bag CR 0 picker regression failed",error);
  process.exitCode=1;
}