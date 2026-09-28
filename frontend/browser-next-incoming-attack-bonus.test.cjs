"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-modifiers.js", "browser-state.js",
  "browser-rage.js", "browser-sneak-attack.js", "browser-rolls.js", "browser-undead-fortitude.js",
  "browser-zero-hp.js", "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-attack.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll(sides) {
      const value = rolls.shift();
      if (!(value >= 1 && value <= sides)) throw new Error(`invalid d${sides}: ${value}`);
      return value;
    },
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
}

function member(id) {
  const template = structuredClone(base);
  template.id = `template-${id}`;
  template.name = id;
  template.armor_class = 18;
  return { combatant_id: id, side: id === "target" ? "monsters" : "heroes", position_ft: 0, state: S.buildState(template) };
}

function attack(attacker, target, values, sequence) {
  dice(values);
  return window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
    sequence, 1, attacker, target, attacker.state.template.attacks[0], 5, { spendAction: false },
  );
}

{
  const source = member("source"), ally = member("ally"), target = member("target");
  M.add(target.state, {
    id: "source:sundering:target",
    source_id: source.combatant_id,
    source_effect_id: "sundering-blow",
    source_name: "Sundering Blow",
    kind: "next-incoming-attack-roll-flat",
    flat_bonus: 5,
    expires_at_start_of_source_turn: true,
  });

  assert.equal(M.nextIncomingAttackRollFlat(target.state, source.combatant_id), 0);
  assert.equal(M.nextIncomingAttackRollFlat(target.state, ally.combatant_id), 5);

  const sourceEvent = attack(source, target, [8], 1);
  assert.equal(sourceEvent.hit, false);
  assert.equal(M.nextIncomingAttackRollFlat(target.state, ally.combatant_id), 5);

  const allyEvent = attack(ally, target, [8, 4], 2);
  assert.equal(allyEvent.hit, true);
  assert.equal(allyEvent.attack_roll.modifier, ally.state.template.attacks[0].bonus + 5);
  assert.equal(M.nextIncomingAttackRollFlat(target.state, ally.combatant_id), 0);
}


{
  const target = member("target");
  for (const [sourceId, bonus] of [["source-a", 5], ["source-b", 5], ["source-c", 3]]) {
    M.add(target.state, {
      id: `${sourceId}:incoming`, source_id: sourceId, source_effect_id: "incoming-attack-bonus",
      kind: "next-incoming-attack-roll-flat", flat_bonus: bonus,
    });
  }
  assert.equal(M.nextIncomingAttackRollFlat(target.state, "ally"), 5, "incoming flat bonuses do not stack");
}

console.log("Browser next incoming attack-roll bonus regressions passed.");
