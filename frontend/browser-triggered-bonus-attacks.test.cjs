"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "bonus_action" && state.bonus_action_available,
  spend: (state) => { state.bonus_action_available = false; },
};
window.IRON_PIT_BROWSER_MAX_HP_REDUCTION = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, id, cost) => (state.resources[id] || 0) >= cost,
  spend: (state, id, cost) => (state.resources[id] -= cost),
};
window.IRON_PIT_BROWSER_STATE = { distance: () => 5 };
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, round, member, target, attack, distance, extra) => ({
    sequence, round_number: round, event_type: "attack",
    actor_id: member.combatant_id, actor_name: member.state.template.name,
    target_id: target.combatant_id, target_name: target.state.template.name,
    feature_id: extra.featureId, damage_roll: { total: 5 },
    animation: "strike", description: "Rampage attack",
  }),
};

vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-triggered-bonus-attacks.js"), "utf8"),
  { filename: "browser-triggered-bonus-attacks.js" },
);

const feature = {
  id: "srd-giant-hyena-rampage", name: "Rampage",
  trigger: "damage_target_already_bloodied",
  attackId: "hyena-bite", resourceId: "srd-giant-hyena-rampage", resourceCost: 1,
};
const hyena = {
  combatant_id: "hyena", side: "monsters", position_ft: 5,
  state: {
    bonus_action_available: true,
    resources: { "srd-giant-hyena-rampage": 1 },
    template: {
      name: "Giant Hyena",
      triggered_bonus_attacks: [feature],
      attacks: [{ id: "hyena-bite", kind: "melee", reach: 5 }],
    },
  },
};
const hero = {
  combatant_id: "hero", side: "heroes", position_ft: 5,
  state: { is_alive: true, is_dead: false, template: { name: "Hero", max_hp: 20 } },
};
const setup = { heroes: [hero], monsters: [hyena] };
const trigger = {
  actor_id: "hyena", target_id: "hero", event_type: "attack",
  damage_roll: { total: 3 }, hp_before: 10, max_hp_before: 20,
};

const result = window.IRON_PIT_BROWSER_TRIGGERED_BONUS_ATTACKS.resolve(
  2, 1, hyena, setup, [trigger], "1:hyena",
);
assert.equal(result.sequence, 3);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_id, feature.id);
assert.equal(hyena.state.bonus_action_available, false);
assert.equal(hyena.state.resources[feature.resourceId], 0);

console.log("Browser triggered Bonus Action Rampage regression passed.");
