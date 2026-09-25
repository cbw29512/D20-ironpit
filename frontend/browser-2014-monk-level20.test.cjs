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

load("browser-heroes.js");
load("browser-initiative-resource-refill.js");

const hero = Object.values(window.IRON_PIT_BROWSER_HEROES)
  .find((item) => item.id === "kael-stillwater-2014-l20");

assert.ok(hero, "certified 2014 Monk level 20 must be exported");
assert.deepEqual(hero.ability_scores, {
  strength: 14, dexterity: 20, constitution: 14,
  intelligence: 11, wisdom: 20, charisma: 9,
});
assert.equal(hero.armor_class, 20);
assert.equal(hero.max_hp, 143);
assert.equal(hero.speed_ft, 60);
assert.equal(hero.resources.ki, 20);
assert.equal(hero.deferred_save_effect.save_dc, 19);
assert.equal(hero.opening_targeting_ward.save_dc, 19);
assert.equal(hero.timed_self_buff_actions[0].id, "empty-body");
assert.deepEqual(hero.initiative_resource_refill_grants, [{
  source_id: "perfect-self",
  source_name: "Perfect Self",
  resource_id: "ki",
  when_at_or_below: 0,
  restore_amount: 4,
}]);

const member = {
  combatant_id: "kael",
  state: {
    template: hero,
    resources: { ...hero.resources, ki: 0 },
  },
};
const target = {
  combatant_id: "target",
  state: {
    template: { name: "Target", resources: {}, initiative_resource_refill_grants: [] },
    resources: {},
  },
};
const result = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
  3, { heroes: [member], monsters: [target] },
);
assert.equal(member.state.resources.ki, 4);
assert.equal(result.events[0].feature_id, "perfect-self");
assert.equal(result.events[0].resource_remaining, 4);
assert.match(result.events[0].description, /Perfect Self/);

member.state.resources.ki = 1;
const inactive = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
  4, { heroes: [member], monsters: [target] },
);
assert.deepEqual(inactive.events, []);
assert.equal(member.state.resources.ki, 1);

console.log("2014 Monk level 20 Perfect Self browser data and refill behavior are certified.");
