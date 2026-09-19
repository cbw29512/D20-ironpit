"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
for (const file of ["browser-heroes.js", "browser-state.js", "browser-rolls.js", "browser-saves.js",
  "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-modifiers.js",
  "browser-defensive-modifier-rules.js", "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-attack.js"]) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
}
const S = window.IRON_PIT_BROWSER_STATE, Z = window.IRON_PIT_BROWSER_ZERO_HP;
const U = window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE;
let rolls = [];
window.IRON_PIT_DICE = { roll(sides) {
  assert.ok(rolls.length, "unexpected die roll");
  const result = rolls.shift(); assert.ok(result >= 1 && result <= sides); return result;
} };
function candidate(level = 11) {
  const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l6"]);
  assert.ok(template, "certified baseline exists");
  template.saving_throw_bonuses.constitution = 7;
  template.max_hp = 115; template.level = level;
  template.effect_bound_survival_save = { source_id: "relentless-rage", required_effect_id: "rage",
    save_ability: "constitution", initial_dc: 10, dc_increment: 5, replacement_hp: level * 2 };
  const state = S.buildState(template);
  state.active_effect_ids.push("rage"); state.current_hp = 1;
  return state;
}
{
  const state = candidate(); rolls = [3];
  assert.equal(Z.applyDamage(state, 1), "survival_save");
  assert.equal(state.current_hp, 22);
  assert.equal(state.is_unconscious, false);
  assert.equal(state.resources["relentless-endurance"], 1);
  assert.equal(state.action_available, true); assert.equal(state.reaction_available, true);
  assert.match(U.consumeLog(state), /DC 10.*total 10.*succeeds.*next DC 15/);
  assert.equal(U.consumeLog(state), "");
  state.current_hp = 1; rolls = [1];
  assert.equal(Z.applyDamage(state, 1), "relentless_endurance");
  assert.equal(state.survival_save_uses["relentless-rage"], 2);
  assert.match(U.consumeLog(state), /DC 15.*fails.*next DC 20/);
  rolls = [13]; assert.equal(Z.applyDamage(state, 1), "survival_save");
  assert.equal(state.current_hp, 22);
  assert.deepEqual(S.buildState(state.template).survival_save_uses, {});
  assert.equal(state.template.effect_bound_survival_save.initial_dc, 10);
}
for (const kind of ["no-rage", "instant-death", "already-zero", "temp-hp"]) {
  const state = candidate(); rolls = []; let amount = 1;
  if (kind === "no-rage") state.active_effect_ids = [];
  if (kind === "instant-death") amount = 116;
  if (kind === "already-zero") state.current_hp = 0;
  if (kind === "temp-hp") state.temporary_hp = 2;
  Z.applyDamage(state, amount);
  assert.deepEqual(state.survival_save_uses, {});
  if (kind === "instant-death") assert.equal(state.is_dead, true);
}
{
  const state = candidate(20); rolls = [3];
  assert.equal(Z.applyDamage(state, 1, true, ["radiant"]), "survival_save");
  assert.equal(state.current_hp, 40);
}
{
  const state = candidate(); state.resources["relentless-endurance"] = 0; rolls = [1];
  assert.equal(Z.applyDamage(state, 1), "unconscious");
  assert.equal(state.is_unconscious, true);
}
{
  const state = candidate(); rolls = [1];
  state.active_modifiers.push({ id: "save-boost", source_id: "ally", source_effect_id: "test-buff",
    kind: "saving-throw-flat", flat_bonus: 2 });
  assert.equal(Z.applyDamage(state, 1), "survival_save");
  assert.match(U.consumeLog(state), /modifier 9, total 10/);
}
{
  const target = { combatant_id: "target", state: candidate() };
  const actor = { combatant_id: "source", state: candidate() };
  rolls = [1, 4, 3];
  window.IRON_PIT_DICE.rollMany = (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides));
  const event = window.IRON_PIT_BROWSER_SAVES.resolveAction(1, 1, actor, target,
    { id: "fire", name: "Fire", saveAbility: "dexterity", dc: 15, range: 30,
      damageDiceCount: 1, damageDiceSize: 6, damageType: "fire", successDamage: "half" }, 5);
  assert.equal(event.save_ability, "dexterity"); assert.equal(event.save_dc, 15);
  assert.equal(event.save_succeeded, false); assert.equal(event.hp_after, 22);
  assert.match(event.description, /relentless-rage: DC 10 constitution/);
  assert.deepEqual(target.state.pending_survival_save_logs, []);
}
console.log("Effect-bound survival browser regressions passed.");
