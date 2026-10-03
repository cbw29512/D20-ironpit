"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync("frontend/" + name, "utf8"), { filename: name },
);

try {
  for (const file of [
    "browser-heroes.js", "browser-condition-rules.js", "browser-modifiers.js",
    "browser-timed-conditions.js", "browser-grid-geometry.js", "browser-state.js", "browser-action-economy.js",
    "browser-resources.js", "browser-spellcasting.js", "browser-timed-self-buff-policy.js",
    "browser-timed-self-buffs.js", "browser-friendly-save-auras.js",
    "browser-attack-outcome.js", "browser-ability-hooks.js", "browser-post-hit-damage.js",
  ]) load(file);

  const registry = window.IRON_PIT_BROWSER_HEROES;
  const hero = registry["aurelia-brightshield-l15"];
  const previous = registry["aurelia-brightshield-l14"];
  assert.ok(hero && previous);
  assert.equal(hero.name, previous.name);
  assert.deepEqual(hero.ability_scores, previous.ability_scores);
  assert.equal(hero.max_hp, 124);
  assert.equal(hero.resources["lay-on-hands"], 75);
  assert.equal(hero.resources["spell-slot-4"], 2);
  assert.equal(hero.canonical_prepared_spells.length, 12);
  assert.equal(hero.canonical_prepared_spells.at(-1).id, "aura-of-life");
  assert.equal(hero.resource_backed_post_hit_damage.post_hit_self_buff_action_id, "smite-of-protection-2024");
  const action = hero.timed_self_buff_actions.find(item => item.id === "smite-of-protection-2024");
  assert.ok(action);
  assert.deepEqual(action.friendlyCoverAura, { radius_ft: 10, cover_bonus: 2 });

  const S = window.IRON_PIT_BROWSER_STATE;
  const M = window.IRON_PIT_BROWSER_MODIFIERS;
  const O = window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
  const P = window.IRON_PIT_BROWSER_POST_HIT_DAMAGE;
  const A = window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS;

  const aurelia = { combatant_id: "aurelia", side: "heroes", position_ft: 0, state: S.buildState(hero) };
  const allyTemplate = { ...registry["kael-stillwater-l1"], armor_class: 10 };
  const ally = { combatant_id: "ally", side: "heroes", position_ft: 5, state: S.buildState(allyTemplate) };
  const enemy = { combatant_id: "enemy", side: "monsters", position_ft: 10, state: S.buildState(allyTemplate) };
  aurelia.state.position = { x: 0, y: 0 };
  ally.state.position = { x: 1, y: 0 };
  enemy.state.position = { x: 2, y: 0 };
  const setup = { heroes: [aurelia, ally], monsters: [enemy] };

  const outcome = O.create();
  outcome.damageComponents = [{ source: "Longsword" }, { source: "Divine Smite" }];
  const result = P.activateTriggeredBuff({
    sequence: 1, round: 1, member: aurelia, setup, attackOutcome: outcome,
  });
  assert.deepEqual(result, { events: [], sequence: 1, claimed: false });
  assert.equal(outcome.postHitSelfBuffApplied.sourceName, "Smite of Protection");
  assert.ok(aurelia.state.timed_effects.some(effect =>
    effect.source_effect_id === "smite-of-protection-2024"
    && effect.expires_round === 2
    && effect.expiry_timing === "source_turn_start"
  ));
  assert.equal(M.effectiveArmorClass(aurelia.state), hero.armor_class + 2);
  assert.equal(M.effectiveArmorClass(ally.state), 12);
  assert.equal(M.savingThrowFlat(ally.state, "dexterity"), 5);
  assert.equal(M.savingThrowFlat(ally.state, "wisdom"), 3);
  assert.equal(M.effectiveArmorClass(enemy.state), 10);

  ally.state.position = { x: 3, y: 0 };
  A.sync(setup);
  assert.equal(M.effectiveArmorClass(ally.state), 10);
  ally.state.position = { x: 1, y: 0 };
  A.sync(setup);
  assert.equal(M.effectiveArmorClass(ally.state), 12);

  const noSmite = O.create();
  noSmite.damageComponents = [{ source: "Longsword" }];
  assert.equal(P.activateTriggeredBuff({
    sequence: 2, round: 1, member: aurelia, setup, attackOutcome: noSmite,
  }), null);
  assert.equal(noSmite.postHitSelfBuffApplied, null);

  const coverState = S.buildState(allyTemplate);
  M.add(coverState, {
    id: "normal-ac", source_id: "spell", source_effect_id: "spell",
    kind: "armor-class", flat_bonus: 2,
  });
  for (const [id, bonus] of [["half", 2], ["three-quarters", 5]]) {
    M.add(coverState, {
      id: "ac-" + id, source_id: id, source_effect_id: "cover",
      kind: "cover-armor-class", flat_bonus: bonus,
    });
    M.add(coverState, {
      id: "save-" + id, source_id: id, source_effect_id: "cover",
      kind: "cover-saving-throw-flat", flat_bonus: bonus, save_ability: "dexterity",
    });
  }
  M.add(coverState, {
    id: "normal-save", source_id: "buff", source_effect_id: "buff",
    kind: "saving-throw-flat", flat_bonus: 3,
  });
  assert.equal(M.effectiveArmorClass(coverState), 17);
  assert.equal(M.savingThrowFlat(coverState, "dexterity"), 8);
  assert.equal(M.savingThrowFlat(coverState, "wisdom"), 3);

  window.IRON_PIT_BROWSER_TIMED.expireSourceStart(2, 2, aurelia, setup);
  A.sync(setup);
  assert.equal(M.effectiveArmorClass(ally.state), 10);

  const hook = window.IRON_PIT_BROWSER_ABILITY_HOOKS
    .abilitiesFor(window.IRON_PIT_BROWSER_ABILITY_HOOKS.PHASES.ON_HIT)
    .find(item => item.id === "resource-backed-post-hit-self-buff");
  assert.ok(hook);

  console.log("2024 Paladin 15 Smite of Protection and strongest-cover parity passed.");
} catch (error) {
  console.error("2024 Paladin 15 browser parity failed.", error);
  throw error;
}
