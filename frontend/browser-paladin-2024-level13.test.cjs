"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;

try {
  for (const file of ["browser-heroes.js", "browser-opening-modifiers.js", "browser-debuff-counters.js",
    "browser-condition-immunity.js", "browser-condition-rules.js", "browser-modifier-validation.js", "browser-modifiers.js",
    "browser-grapple.js", "browser-timed-conditions.js", "browser-state.js", "browser-spell-modifiers.js",
    "browser-precombat-spells.js", "browser-action-economy.js", "browser-resources.js",
    "browser-spellcasting.js", "browser-post-hit-damage.js", "browser-rolls.js"]) {
    vm.runInThisContext(fs.readFileSync(`frontend/${file}`, "utf8"), { filename: file });
  }
  const registry = window.IRON_PIT_BROWSER_HEROES;
  const hero = registry["aurelia-brightshield-l13"];
  const previous = registry["aurelia-brightshield-l12"];
  assert.equal(hero.ruleset, "2024");
  assert.equal(hero.name, previous.name);
  assert.deepEqual(hero.ability_scores, previous.ability_scores);
  assert.equal(hero.max_hp, 108);
  assert.equal(hero.attacks.find(a => a.id === hero.primary_attack_id).bonus, 10);
  assert.equal(hero.saving_throw_bonuses.charisma, 8);
  assert.equal(hero.skill_bonuses.persuasion, 8);
  assert.equal(hero.saving_throw_actions[0].dc, 16);
  assert.equal(hero.saving_throw_actions[0].maxTargets, 3);
  assert.equal(hero.resources["lay-on-hands"], 65);
  assert.equal(hero.resources["spell-slot-4"], 1);
  assert.equal(hero.canonical_prepared_spells.length, 11);
  assert.equal(hero.canonical_prepared_spells.at(-1).id, "staggering-smite");
  assert.equal(hero.persistent_hazard_actions.length, 0);
  assert.deepEqual(hero.canonical_prepared_spells.at(-1).requiredCapabilities, ["arena-out-of-scope"]);
  assert.deepEqual(hero.canonical_always_prepared_spells.find(s => s.id === "guardian-of-faith").requiredCapabilities,
    ["arena-unavailable-summon"]);
  assert.deepEqual(hero.resource_backed_post_hit_damage, previous.resource_backed_post_hit_damage);
  const spell = hero.defensive_spell_actions.find(s => s.id === "freedom-of-movement");
  assert.equal(spell.targetCountPerSlotAbove, 1);
  assert.deepEqual(spell.movementModeGrants, [{ mode: "swim", fixedSpeedFt: null, matchCurrentSpeed: true }]);
  assert.equal(hero.defensive_spell_actions.some(s => s.id === "death-ward"), false);

  const S = window.IRON_PIT_BROWSER_STATE;
  const P = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
  const C = window.IRON_PIT_BROWSER_DEBUFF_COUNTERS;
  const member = { combatant_id: "aurelia", side: "heroes", position_ft: 0, state: S.buildState(hero) };
  const setup = { heroes: [member], monsters: [] };
  const choice = P.choose(member, setup);
  assert.equal(choice.spell.id, "freedom-of-movement");
  const event = P.resolve(1, member, [member], choice.spell, choice.slotLevel, [member.state]);
  assert.equal(event.feature_id, "freedom-of-movement");
  assert.equal(member.state.resources["spell-slot-4"], 0);
  assert.equal(member.state.concentration, null);
  assert.equal(S.effectiveMovementModes(member.state).swim_ft, 30);
  assert.equal(C.prevented(member.state, "paralyzed", { sourceIsMagical: true }), true);
  assert.equal(C.prevented(member.state, "paralyzed", { sourceIsMagical: false }), false);
  window.IRON_PIT_BROWSER_GRAPPLE.apply(member.state, "monster", 12, 5, true, false);
  assert.deepEqual(S.beginTurn(member.state), [{ debuffId: "restrained", sourceId: "monster", movementCost: 5 }]);
  assert.equal(member.state.movement_remaining_ft, 25);
  assert.equal(member.state.grapple_sources.length, 0);
  assert.equal(P.choose(member, setup), null);
  window.IRON_PIT_BROWSER_TIMED.expireSourceStart(2, 601, member, setup);
  assert.equal(C.prevented(member.state, "paralyzed", { sourceIsMagical: true }), false);
  assert.equal(S.effectiveMovementModes(member.state).swim_ft, 0);
  assert.equal(member.state.timed_effects.some(e => e.owned_movement_mode_grants?.length), false);
  const fresh = S.buildState(hero);
  assert.equal(fresh.resources["spell-slot-4"], 1);
  assert.equal(fresh.opening_buff_id, null);
  assert.equal(fresh.current_hp, 108);
  assert.deepEqual(fresh.timed_effects, []);
  assert.equal(previous.resources["spell-slot-4"], undefined);
  // The printed Melee weapon category qualifies a ranged thrown Javelin hit.
  const thrown = hero.attacks.find(a => a.weaponId === "javelin");
  assert.equal(thrown.kind, "ranged");
  const attacker = S.buildState(hero);
  attacker.feature_last_turn_keys["savage-attacker"] = "1:aurelia";
  const target = S.buildState(registry["kael-stillwater-l1"]);
  window.IRON_PIT_DICE = {
    rolls: [3, 4, 5, 6, 7, 8, 1, 2],
    roll() { if (!this.rolls.length) throw new Error("Queued damage dice exhausted."); return this.rolls.shift(); },
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
  const hit = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(attacker, thrown, true, "normal", "1:aurelia", null, target);
  assert.deepEqual(hit.components.map(c => [c.source, c.notation]), [
    ["Javelin", "2d6+5"], ["Radiant Strikes", "2d8+0"], ["Divine Smite", "4d8+0"],
  ]);
  assert.equal(hit.roll.total, 41);
  assert.equal(attacker.bonus_action_available, false);
  assert.equal(attacker.resources["paladins-smite-free-cast"], 0);
  assert.equal(attacker.resources["spell-slot-4"], 1);
  assert.equal(attacker.spell_slot_expended_turn_key, null);
  console.log("2024 Paladin 13 source and shared opening movement spell parity passed.");
} catch (error) {
  console.error("2024 Paladin 13 browser parity failed.", error);
  throw error;
}
