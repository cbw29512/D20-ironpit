"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-beast2.js", "browser-state.js",
  "browser-action-economy.js", "browser-healing.js", "browser-charge.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const E = window.IRON_PIT_ACTION_ECONOMY;
const H = window.IRON_PIT_BROWSER_HEALING;
const heroTemplate = () => structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const member = (id) => ({ combatant_id: id, side: "heroes", position_ft: 0, state: S.buildState(heroTemplate()) });
const setup = (healer, ally) => ({ heroes: [healer, ally], monsters: [] });

{
  const hero = member("hero-1");
  assert.equal(E.available(hero.state, "reaction"), true);
  E.spend(hero.state, "reaction");
  assert.equal(E.available(hero.state, "reaction"), false);
  assert.throws(() => E.spend(hero.state, "reaction"));
  S.beginTurn(hero.state);
  assert.equal(E.available(hero.state, "reaction"), true);
}

{
  const hero = member("hero-1");
  hero.state.active_effect_ids.push("incapacitated");
  for (const cost of ["action", "bonus_action", "reaction"]) {
    assert.equal(E.available(hero.state, cost), false);
    assert.throws(() => E.spend(hero.state, cost));
  }
}

{
  const healer = member("hero-1"), ally = member("hero-2");
  healer.state.current_hp = Math.floor(healer.state.template.max_hp / 2);
  ally.state.current_hp = 0; ally.state.is_unconscious = true; ally.state.death_save_failures = 2;
  const action = { id: "test-heal", name: "Test Heal", actionCost: "bonus_action", range: 60,
    targetMode: "self_or_ally", diceCount: 1, diceSize: 4, healingBonus: 3 };
  healer.state.template.healingActions = [action];
  const choice = H.chooseAction(healer, setup(healer, ally));
  assert.equal(choice.target.combatant_id, ally.combatant_id);
  window.IRON_PIT_DICE = { roll: () => 4 };
  const event = H.resolve(1, 1, healer, ally, action);
  assert.equal(event.hp_before, 0);
  assert.equal(event.hp_after, 7);
  assert.equal(ally.state.is_unconscious, false);
  assert.equal(ally.state.death_save_failures, 0);
  assert.equal(healer.state.action_available, true);
  assert.equal(healer.state.bonus_action_available, false);
}

{
  const healer = member("hero-1"), ally = member("hero-2");
  healer.state.current_hp = 1;
  ally.state.current_hp = Math.floor(ally.state.template.max_hp / 2);
  const action = { id: "ally-heal", name: "Ally Heal", actionCost: "action", range: 5,
    targetMode: "self_or_ally", diceCount: 0, diceSize: 6, healingBonus: 5 };
  assert.equal(H.chooseTarget(healer, setup(healer, ally), action).combatant_id, ally.combatant_id);
}

{
  const healer = member("hero-1"), ally = member("hero-2"), fight = setup(healer, ally);
  const actionHeal = { id: "action-heal", name: "Action Heal", actionCost: "action", range: 5,
    targetMode: "self", diceCount: 0, diceSize: 6, healingBonus: 5 };
  const bonusHeal = { id: "bonus-heal", name: "Bonus Heal", actionCost: "bonus_action", range: 5,
    targetMode: "self", diceCount: 0, diceSize: 6, healingBonus: 5 };
  healer.state.current_hp = Math.floor(healer.state.template.max_hp / 2);
  assert.equal(H.chooseTarget(healer, fight, actionHeal), null);
  assert.equal(H.chooseTarget(healer, fight, bonusHeal).combatant_id, healer.combatant_id);
  healer.state.current_hp = Math.max(1, Math.floor(healer.state.template.max_hp / 4));
  assert.equal(H.chooseTarget(healer, fight, actionHeal).combatant_id, healer.combatant_id);
}

{
  const healer = member("hero-1"), ally = member("hero-2");
  ally.state.current_hp = 1;
  healer.state.template.healingActions = [{ id: "reaction-heal", name: "Reaction Heal", actionCost: "reaction", range: 60,
    targetMode: "ally", diceCount: 0, diceSize: 6, healingBonus: 5 }];
  assert.equal(H.chooseAction(healer, setup(healer, ally)), null);
}

{
  const target = member("hero-1");
  const goat = {
    combatant_id: "monster-1:giant-goat", side: "monsters", position_ft: 30,
    state: S.buildState(structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-giant-goat"])),
  };
  S.beginTurn(goat.state);
  goat.state.current_hp = 1;
  const heal = { id: "self-heal", name: "Self Heal", actionCost: "action", range: 5,
    targetMode: "self", diceCount: 0, diceSize: 6, healingBonus: 5 };
  H.resolve(1, 1, goat, goat, heal);
  const before = goat.position_ft;
  const result = window.IRON_PIT_BROWSER_CHARGE.resolveClosing(2, 1, goat, target);
  assert.equal(result.handled, false);
  assert.deepEqual(result.events, []);
  assert.equal(goat.position_ft, before);
  assert.equal(goat.state.action_available, false);
}

console.log("Browser action economy and healing AI regressions passed.");
