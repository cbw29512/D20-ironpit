"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
load("browser-attachments.js");
load("browser-attachment-turn.js");
const A = window.IRON_PIT_BROWSER_ATTACHMENTS;
const Turn = window.IRON_PIT_BROWSER_ATTACHMENT_TURN;

window.IRON_PIT_DICE = {
  rolls: [],
  roll(size) {
    const value = this.rolls.shift();
    if (!Number.isInteger(value) || value < 1 || value > size) throw Error("Invalid queued die.");
    return value;
  },
};
window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN = {
  loseHitPoints(state, amount) {
    const actual = Math.min(state.current_hp, amount);
    state.current_hp -= actual;
    if (state.current_hp <= 0) { state.is_alive = false; state.is_dead = true; }
    return actual;
  },
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage(_state, total, _type) { return { applied: total }; },
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage(state, amount) {
    const shield = Math.min(state.temporary_hp, amount);
    state.temporary_hp -= shield;
    state.current_hp -= amount - shield;
  },
};
const member = (id, side) => ({
  combatant_id: id, side, state: {
    template: { name: id }, current_hp: 20, temporary_hp: 9,
    is_alive: true, is_dead: false, active_effect_ids: [],
  },
});
const setup = () => {
  const source = member("source", "monsters"), victim = member("victim", "heroes");
  const encounter = { heroes: [victim], monsters: [source], attachments: [] };
  return { source, victim, encounter };
};
const link = (kind = "direct_hp_loss", type = null) => ({
  source_id: "source", target_id: "victim", effect_id: "periodic",
  source_name: kind === "direct_hp_loss" ? "Blood Drain" : "Synthetic Drain",
  periodic_effect_kind: kind, damage_dice_count: 1, damage_dice_size: 4,
  damage_bonus: 3, damage_type: type, damage_timing: "source_turn_start",
  detach_after_hp_lost: kind === "direct_hp_loss" ? 10 : null,
});
{
  const { source, victim, encounter } = setup();
  encounter.attachments = A.attach([], link());
  window.IRON_PIT_DICE.rolls = [1, 4];
  let result = Turn.resolve(1, 1, source, encounter);
  assert.equal(result.sequence, 2);
  assert.equal(victim.state.current_hp, 16);
  assert.equal(victim.state.temporary_hp, 9, "Direct HP loss bypasses temp HP.");
  assert.deepEqual(victim.state.active_effect_ids, [], "Attachment does not apply Grappled.");
  assert.equal(encounter.attachments[0].actual_hp_lost, 4);
  assert.equal(result.events[0].feature_id, "Blood Drain");
  assert.deepEqual(result.events[0].damage_components, []);
  result = Turn.resolve(2, 2, source, encounter);
  assert.equal(result.sequence, 3);
  assert.equal(victim.state.current_hp, 9);
  assert.deepEqual(encounter.attachments, []);
  assert.deepEqual(window.IRON_PIT_DICE.rolls, []);
}
{
  const { source, victim, encounter } = setup();
  encounter.attachments = A.attach([], link("typed_damage", "necrotic"));
  window.IRON_PIT_DICE.rolls = [2];
  const result = Turn.resolve(1, 1, source, encounter);
  assert.equal(victim.state.current_hp, 20);
  assert.equal(victim.state.temporary_hp, 4);
  assert.equal(encounter.attachments[0].actual_hp_lost, 0);
  assert.deepEqual(result.events[0].damage_components[0].rolls, [2]);
  assert.match(result.events[0].description, /necrotic damage/);
}
{
  const { source, encounter } = setup();
  encounter.attachments = A.attach([], link());
  source.state.is_dead = true; source.state.is_alive = false;
  assert.deepEqual(Turn.resolve(1, 1, source, encounter).events, []);
  assert.deepEqual(encounter.attachments, []);
}
console.log("Browser attachment turn integration tests passed.");
