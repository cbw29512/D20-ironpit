"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-rules.js", "browser-action-economy.js", "browser-modifiers.js",
  "browser-state.js", "browser-spellcasting.js", "browser-healing.js", "browser-spell-area.js",
  "browser-rolls.js", "browser-attack.js", "browser-saves.js", "browser-offense-value.js",
  "browser-spell-policy.js", "browser-spell-attack-policy.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const H = window.IRON_PIT_BROWSER_HEALING;
const A = window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
const V = window.IRON_PIT_BROWSER_SPELL_POLICY;
const word = {
  id: "healing-word", name: "Healing Word", actionCost: "bonus_action", range: 60,
  targetMode: "self_or_ally", diceCount: 2, diceSize: 4, healingBonus: 3,
  resourceId: "spell-slot-1", resourceCost: 1, animation: "healing",
};

function member(templateId, id, side, position) {
  return { combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(window.IRON_PIT_BROWSER_HEROES[templateId])) };
}

function setup() {
  const caster = member("seraphine-dawnshield-l1", "cleric", "heroes", 0);
  const ally = member("karnok-stoneward-l1", "ally", "heroes", 5);
  const enemy = member("karnok-stoneward-l1", "enemy", "monsters", 10);
  caster.state.template.healingActions.push(word);
  ally.state.current_hp = 1;
  return { fight: { heroes: [caster, ally], monsters: [enemy] }, caster, ally };
}

{
  const { fight, caster, ally } = setup(), turnKey = "1:cleric";
  const choice = H.chooseAction(caster, fight, turnKey);
  assert.equal(choice.action.id, "healing-word"); assert.equal(choice.target.combatant_id, "ally");
  const rolls = [4, 3]; window.IRON_PIT_DICE = { roll: () => rolls.shift() };
  const event = H.resolve(1, 1, caster, ally, choice.action, turnKey);
  assert.equal(event.healing_roll.total, 10);
  assert.equal(caster.state.bonus_action_available, false); assert.equal(caster.state.action_available, true);
  assert.equal(caster.state.spell_slot_expended_turn_key, turnKey);
  assert.equal(A.choose(caster, fight, turnKey), null);
  const cantrip = V.choose(caster, fight, turnKey);
  assert.equal(cantrip.action.id, "sacred-flame"); assert.equal(cantrip.slotLevel, 0);
}

{
  const { fight, caster } = setup(), turnKey = "1:cleric";
  caster.state.spell_slot_expended_turn_key = turnKey;
  assert.equal(H.chooseAction(caster, fight, turnKey), null);
}

{
  const { fight, caster } = setup();
  assert.equal(H.chooseAction(caster, fight), null);
}

console.log("Browser spell-slot healing turn gate regression passed.");
