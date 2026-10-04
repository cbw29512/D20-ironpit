"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

for (const file of [
  "browser-heroes.js",
  "browser-condition-rules.js",
  "browser-action-economy.js",
  "browser-modifier-validation.js", "browser-modifiers.js",
  "browser-state.js",
  "browser-rolls.js",
  "browser-ability-hooks.js",
  "browser-attack-outcome.js",
  "browser-attack.js",
  "browser-offense-value.js",
  "browser-spellcasting.js",
  "browser-spell-area.js",
  "browser-spell-policy-support.js", "browser-spell-policy.js",
  "browser-spell-attack-policy.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const P = window.IRON_PIT_BROWSER_SPELL_POLICY;
const A = window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function member(id, side, position, template) {
  return {
    combatant_id: id,
    side,
    position_ft: position,
    state: S.buildState(structuredClone(template)),
  };
}

function sorcerer(position = 0) {
  const template = structuredClone(base);
  template.id = "range-caster";
  template.name = "Range Caster";
  template.resources = { "sorcery-points": 10 };
  template.spellRangeModifiers = [{
    id: "distant-spell",
    name: "Distant Spell",
    resourceId: "sorcery-points",
    resourceCost: 1,
    rangeMultiplier: 2,
    minimumBaseRangeFt: 5,
    priority: 100,
  }];
  template.spell_attack_actions = [{
    id: "fire-bolt",
    name: "Fire Bolt",
    level: 0,
    actionCost: "action",
    attackKind: "ranged",
    range: 120,
    attackBonus: 8,
    damageDiceCount: 2,
    damageDiceSize: 10,
    damageBonus: 5,
    damageType: "fire",
    onHitModifierEffects: [],
  }];
  return member("caster", "heroes", position, template);
}

{
  const caster = sorcerer();
  assert.equal(P.effectiveRange(caster.state, 120), 240);
  assert.equal(P.availableRangeModifier(caster.state, 120, 100), null);
  assert.equal(P.availableRangeModifier(caster.state, 120, 200).id, "distant-spell");
}

{
  const caster = sorcerer();
  const target = member("target", "monsters", 200, base);
  const choice = A.choose(caster, { heroes: [caster], monsters: [target] }, "1:caster");
  assert.ok(choice);
  assert.equal(choice.action.id, "fire-bolt");
  assert.equal(choice.rangeModifier.id, "distant-spell");
  assert.equal(caster.state.resources["sorcery-points"], 10);
  assert.equal(P.spendRangeModifier(caster.state, choice.rangeModifier), 9);
}

{
  const caster = sorcerer();
  const target = member("target", "monsters", 100, base);
  const choice = A.choose(caster, { heroes: [caster], monsters: [target] }, "1:caster");
  assert.ok(choice);
  assert.equal(choice.rangeModifier, null);
}
