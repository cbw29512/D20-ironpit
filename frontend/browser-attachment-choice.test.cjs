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
load("browser-attachment-removal.js");
load("browser-attachment-choice.js");
const A = window.IRON_PIT_BROWSER_ATTACHMENTS;
const Choice = window.IRON_PIT_BROWSER_ATTACHMENT_CHOICE;
window.IRON_PIT_ACTION_ECONOMY = {
  available: (s, cost) => cost === "action" && s.action_available,
  spend: (s) => { if (!s.action_available) throw Error("Action missing"); s.action_available = false; },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
const member = (id, side, pos) => ({
  combatant_id: id, side, position_ft: pos,
  state: { is_alive: true, is_dead: false, action_available: true,
    template: { name: id }, movement_remaining_ft: 30 },
});
const attacker = member("parasite", "monsters", 0);
const victim = member("hero", "heroes", 35);
const ally = member("ally", "heroes", 5);
const link = A.validate({
  source_id: "parasite", target_id: "hero", effect_id: "attached",
  source_name: "Printed Source", periodic_effect_kind: "direct_hp_loss",
  damage_type: null, damage_dice_count: 1, damage_dice_size: 4, damage_bonus: 3,
  blocks_source_attacks: true, action_removable: true, action_removal_range_ft: 5,
  source_detach_movement_ft: 5, detach_after_hp_lost: 10,
});
const setup = { heroes: [victim, ally], monsters: [attacker], attachments: A.attach([], link) };
const selected = Choice.choose(victim, setup);
assert.equal(selected.sourceId, "parasite");
assert.equal(selected.targetId, "hero");
assert.equal(selected.sourceName, "Printed Source");
assert.ok(Choice.choose(ally, setup));
assert.equal(Choice.choose(attacker, setup), null, "Enemy cannot remove ally parasite for target.");
const done = Choice.resolve(1, 2, victim, setup, selected);
assert.equal(done.sequence, 2);
assert.equal(victim.state.action_available, false);
assert.deepEqual(setup.attachments, []);
assert.equal(done.events[0].feature_id, "Printed Source");
assert.deepEqual(done.events[0].attachment_changes, [{
  operation: "detach", source_id: "parasite", target_id: "hero",
  effect_id: "attached", source_name: "Printed Source",
}]);
assert.equal(Choice.choose(victim, setup), null);
console.log("Generic browser attachment Action fallback and receipt test passed.");
