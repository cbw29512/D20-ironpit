"use strict";
// Browser parity for 2014 Knight Leadership via TimedFriendlyRollBonusAura.
// Mirrors backend/tests/test_2014_knight_leadership_runtime.py.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const roster = window.IRON_PIT_BROWSER_MONSTERS_2014;
const S = window.IRON_PIT_BROWSER_STATE;
const knightTemplate = roster["2014-knight"];
assert.ok(knightTemplate, "Knight must be admitted to the 2014 browser roster");
const [action] = knightTemplate.timed_self_buff_actions;
assert.equal(action.name, "Leadership");
assert.equal(action.resourceId, "leadership");
assert.equal(action.durationRounds, 10);
assert.equal(action.endsIfSourceIncapacitated, false);
assert.equal(action.endsIfSourceDead, true);
assert.ok(!action.concentration);
assert.deepEqual(action.friendlyRollBonusAura, {
  attack_dice_count: 1, attack_dice_size: 4, includes_source: true, radius_ft: 30,
  requires_hearing: true, requires_source_sight: true, save_dice_count: 1, save_dice_size: 4,
  stack_group: "leadership",
});

const member = (id, side, template, x) => {
  const state = S.buildState(template);
  state.position = { x, y: 7 };
  return { combatant_id: id, side, position_ft: x * 5, state };
};
const knight = member("knight", "monsters", knightTemplate, 1);
const knight2 = member("knight2", "monsters", knightTemplate, 2);
const ally = member("ally", "monsters", roster["2014-commoner"], 4);
const far = member("far", "monsters", roster["2014-commoner"], 10);
const foe = member("foe", "heroes", roster["2014-commoner"], 3);
const setup = { heroes: [foe], monsters: [knight, knight2, ally, far], save_zones: [], map_definition: {} };
assert.equal(knight.state.resources.leadership, 1);

const T = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS;
const sync = () => window.IRON_PIT_BROWSER_FRIENDLY_ROLL_BONUS_AURAS.sync(setup);
const kinds = (m) => m.state.active_modifiers
  .filter((x) => String(x.id).startsWith("friendly-roll-bonus-aura:")).map((x) => x.kind).sort();
S.beginTurn(knight.state);
T.resolve(1, 1, knight, action, { setup, turnKey: "1:knight" });
S.beginTurn(knight2.state);
T.resolve(2, 1, knight2, action, { setup, turnKey: "1:knight2" });
sync();
assert.deepEqual(kinds(ally), ["attack-roll-bonus-die", "saving-throw-bonus-die"], "one Leadership die at a time");
assert.deepEqual(kinds(far), []);
assert.deepEqual(kinds(foe), []);
assert.deepEqual(kinds(knight), ["attack-roll-bonus-die", "saving-throw-bonus-die"]);
assert.equal(knight.state.resources.leadership, 0);
S.beginTurn(knight.state);
assert.throws(() => T.resolve(3, 2, knight, action, { setup, turnKey: "2:knight" }));

ally.state.active_effect_ids.push("deafened");
sync();
assert.deepEqual(kinds(ally), []);
ally.state.active_effect_ids.splice(ally.state.active_effect_ids.indexOf("deafened"), 1);
for (const k of [knight, knight2]) k.state.active_effect_ids.push("blinded");
sync();
assert.deepEqual(kinds(ally), [], "source must see the recipient");
for (const k of [knight, knight2]) {
  k.state.active_effect_ids.splice(k.state.active_effect_ids.indexOf("blinded"), 1);
  k.state.current_hp = 0;
}
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS.cleanupDisabledSources(setup);
sync();
assert.deepEqual(kinds(ally), []);
assert.ok(!(knight.state.timed_effects || []).some((e) => e.source_effect_id === "leadership"));
console.log("browser Knight Leadership parity ok");
