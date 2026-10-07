"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;
try {
  for (const file of ["browser-heroes.js", "browser-opening-modifiers.js", "browser-condition-immunity.js",
    "browser-condition-rules.js", "browser-action-economy.js", "browser-state.js", "browser-grid-geometry.js",
    "browser-timed-conditions.js", "browser-spellcasting.js", "browser-condition-removal-policy.js", "browser-condition-removal.js", "browser-pooled-healing.js",
    "browser-healing-policy.js", "browser-healing-resolution.js", "browser-healing.js", "browser-support.js"]) {
    vm.runInThisContext(fs.readFileSync(`frontend/${file}`, "utf8"), { filename: file });
  }
  const S = window.IRON_PIT_BROWSER_STATE, C = window.IRON_PIT_BROWSER_CONDITION_REMOVAL;
  const H = window.IRON_PIT_BROWSER_HEALING, registry = window.IRON_PIT_BROWSER_HEROES;
  const hero = registry["aurelia-brightshield-l14"], previous = registry["aurelia-brightshield-l13"];
  const restoring = ["blinded", "charmed", "deafened", "frightened", "paralyzed", "stunned"];
  assert.equal(hero.name, previous.name);
  assert.deepEqual(hero.ability_scores, previous.ability_scores);
  assert.equal(hero.max_hp, 116);
  assert.equal(hero.resources["lay-on-hands"], 70);
  assert.deepEqual(hero.canonical_prepared_spells, previous.canonical_prepared_spells);
  assert.deepEqual(hero.resources, { ...previous.resources, "lay-on-hands": 70 });
  const action = hero.condition_removal_actions[0];
  assert.equal(action.maxConditionsPerUse, 7);
  assert.equal(action.actionCost, "bonus_action");
  assert.deepEqual(action.resourceCostsPerCondition, { "lay-on-hands": 5 });
  assert.deepEqual(new Set(action.removableConditions), new Set([...restoring, "poisoned"]));
  assert.deepEqual(previous.condition_removal_actions[0].removableConditions, ["poisoned"]);
  function fixture(template = hero, side = "heroes") {
    const remover = { combatant_id: "aurelia", side, position_ft: 0, state: S.buildState(template) };
    const allyTemplate = { ...registry["kael-stillwater-l1"], max_hp: 4, condition_immunities: [] };
    const ally = { combatant_id: "ally", side, position_ft: 80, state: S.buildState(allyTemplate) };
    remover.state.position = { x: 0, y: 0 }; ally.state.position = { x: 1, y: 0 };
    const setup = { heroes: [], monsters: [] }; setup[side] = [remover, ally];
    return { remover, ally, setup };
  }
  for (const side of ["heroes", "monsters"]) {
    const { remover, ally, setup } = fixture(hero, side);
    ally.state.current_hp = 1;
    ally.state.active_effect_ids = [...restoring, "poisoned", "prone"];
    ally.state.timed_effects = [...restoring, "poisoned"].map(effect_id => ({ effect_id, source_id: "enemy", source_effect_id: effect_id }));
    ally.state.timed_effects.push({ effect_id: "stunned", source_id: "second", source_effect_id: "stunned" });
    const choice = C.chooseAction(remover, setup, "1:aurelia");
    assert.equal(choice.target, ally); assert.equal(choice.conditions.length, 7);
    const event = C.resolve(1, 1, remover, ally, choice.action, choice.conditions, "1:aurelia");
    assert.match(event.description, /Restoring Touch/); assert.equal(event.resource_remaining, 35);
    assert.equal(ally.state.current_hp, 1);
    assert.deepEqual(ally.state.active_effect_ids, ["prone"]); assert.deepEqual(ally.state.timed_effects, []);
    assert.equal(remover.state.resources["lay-on-hands"], 35);
    assert.equal(remover.state.bonus_action_available, false); assert.equal(remover.state.action_available, true);
    assert.equal(remover.state.spell_slot_expended_turn_key, null);
    assert.equal(C.chooseAction(remover, setup, "1:aurelia"), null);
  }
  for (const kind of ["duplicate", "over-cap", "poor", "range", "enemy", "restricted", "incapacitated"]) {
    const { remover, ally } = fixture(); let use = action, ids = ["paralyzed"];
    ally.state.active_effect_ids = ["paralyzed", "deafened"];
    if (kind === "duplicate") ids.push("paralyzed");
    if (kind === "over-cap") { use = { ...action, maxConditionsPerUse: 1 }; ids.push("deafened"); }
    if (kind === "poor") remover.state.resources["lay-on-hands"] = 4;
    if (kind === "range") { ally.state.position = { x: 0, y: 3 }; ally.position_ft = 0; }
    if (kind === "enemy") ally.side = "monsters";
    if (kind === "restricted") ally.state.timed_effects = [{ effect_id: "paralyzed", source_id: "enemy", allowed_removal_action_ids: ["different-remedy"] }];
    if (kind === "incapacitated") remover.state.active_effect_ids = ["stunned"];
    const before = JSON.stringify([remover, ally]);
    assert.throws(() => C.resolve(1, 1, remover, ally, use, ids, "1:aurelia"));
    assert.equal(JSON.stringify([remover, ally]), before, `${kind} mutated state`);
  }
  {
    const { remover, ally, setup } = fixture(); remover.state.resources["lay-on-hands"] = 5;
    ally.state.active_effect_ids = ["paralyzed", "deafened"];
    assert.deepEqual(C.chooseAction(remover, setup, "1:aurelia").conditions, ["paralyzed"]);
    C.resolve(1, 1, remover, ally, action, ["deafened"], "1:aurelia");
    assert.deepEqual(ally.state.active_effect_ids, ["paralyzed"]);
    assert.equal(remover.state.resources["lay-on-hands"], 0);
  }
  {
    const { remover, ally } = fixture(); ally.state.active_effect_ids = ["blinded", "restrained"];
    ally.state.timed_effects = ["blinded", "restrained"].map(effect_id => ({ effect_id, source_id: "enemy", source_effect_id: "group" }));
    ally.state.active_modifiers = [{ id: "owned", source_id: "enemy", source_effect_id: "group", kind: "speed", flat_bonus: -5 }];
    C.resolve(1, 1, remover, ally, action, ["blinded"], "1:aurelia");
    assert.deepEqual(ally.state.active_effect_ids, ["restrained"]); assert.equal(ally.state.active_modifiers.length, 1);
    C.removeCondition(ally, "restrained");
    assert.deepEqual(ally.state.timed_effects, []); assert.deepEqual(ally.state.active_modifiers, []);
  }
  {
    const { remover, ally, setup } = fixture();
    ally.state.template.size = "large"; ally.state.position = { x: 0, y: 1 };
    ally.state.active_effect_ids = ["stunned"];
    const result = window.IRON_PIT_BROWSER_SUPPORT.resolve(1, 1, remover, setup, "1:aurelia");
    assert.deepEqual(result.events[0].removed_condition_ids, ["stunned"]);
    assert.equal(result.events[0].resource_remaining, 65);
    remover.state.bonus_action_available = true;
    ally.state.position = null; ally.position_ft = 0; ally.state.active_effect_ids = ["stunned"];
    const before = JSON.stringify([remover, ally]);
    assert.throws(() => C.chooseAction(remover, setup, "2:aurelia"), /mix scalar and grid/);
    assert.equal(JSON.stringify([remover, ally]), before);
  }
  {
    const { remover, ally } = fixture(); ally.state.current_hp = 1;
    remover.state.action_available = false; remover.state.bonus_action_available = false;
    const before = JSON.stringify([remover, ally]);
    for (const heal of hero.healingActions) {
      assert.throws(() => H.resolve(1, 1, remover, ally, heal, "1:aurelia"));
      assert.equal(JSON.stringify([remover, ally]), before);
    }
  }
  const old = Object.values(registry).find(h => h.name === hero.name && h.ruleset === "2014" && h.level === 14);
  assert.ok(old); assert.deepEqual(old.condition_removal_actions[0].removableConditions, ["poisoned"]);
  for (const template of [old, hero]) {
    const { remover, ally } = fixture(template); const heal = template.healingActions[0];
    assert.equal(heal.healingFromResourcePool, true); const before = JSON.stringify(heal);
    remover.state.resources["lay-on-hands"] = 9; ally.state.current_hp = 1;
    const event = H.resolve(1, 1, remover, ally, heal, "1:aurelia");
    assert.equal(event.healing_roll.total, 3); assert.equal(ally.state.current_hp, 4);
    assert.equal(remover.state.resources["lay-on-hands"], 6); assert.equal(JSON.stringify(heal), before);
    assert.equal(remover.state.bonus_action_available, template.ruleset === "2014");
    assert.equal(remover.state.action_available, template.ruleset === "2024");
    remover.state.action_available = true; remover.state.bonus_action_available = true;
    remover.state.resources["lay-on-hands"] = 2; ally.state.current_hp = 1;
    H.resolve(2, 2, remover, ally, heal, "2:aurelia");
    assert.equal(ally.state.current_hp, 3); assert.equal(remover.state.resources["lay-on-hands"], 0);
  }
  for (const template of [old, hero]) for (const kind of ["undead", "construct"]) {
    const { remover, ally } = fixture(template); ally.state.template.creature_type = kind;
    ally.state.current_hp = 1; ally.state.active_effect_ids = ["poisoned"];
    const use = template.condition_removal_actions[0];
    if (template.ruleset === "2014") {
      const before = JSON.stringify([remover, ally]);
      assert.throws(() => C.resolve(1, 1, remover, ally, use, ["poisoned"], "1:aurelia"));
      assert.throws(() => H.resolve(1, 1, remover, ally, template.healingActions[0], "1:aurelia"));
      assert.equal(JSON.stringify([remover, ally]), before);
    } else {
      C.resolve(1, 1, remover, ally, use, ["poisoned"], "1:aurelia");
      remover.state.bonus_action_available = true;
      H.resolve(2, 2, remover, ally, template.healingActions[0], "2:aurelia");
      assert.equal(ally.state.current_hp, 4); assert.deepEqual(ally.state.active_effect_ids, []);
    }
  }
  const fresh = S.buildState(hero); assert.equal(fresh.current_hp, 116);
  assert.equal(fresh.resources["lay-on-hands"], 70); assert.deepEqual(fresh.timed_effects, []);
  console.log("2024 Paladin 14 Restoring Touch, atomic legality and shared pool parity passed.");
} catch (error) { console.error("Paladin 14 parity failed", error); throw error; }
