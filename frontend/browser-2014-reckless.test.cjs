"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

load("browser-monsters-2014.js");
window.IRON_PIT_BROWSER_TIMED = {
  apply: (state, effectId) => {
    if (!state.active_effect_ids.includes(effectId)) state.active_effect_ids.push(effectId);
    return effectId;
  },
};
load("browser-barbarian2.js");

for (const id of ["2014-berserker", "2014-minotaur"]) {
  const template = window.IRON_PIT_BROWSER_MONSTERS_2014[id];
  assert.ok(template, `${id} must be in the certified 2014 browser roster`);
  assert.ok(template.traits.includes("reckless"));
  assert.ok(template.attacks.length > 0);
  assert.ok(template.attacks.every((attack) => attack.kind === "melee" && attack.attackAbility === "strength"));

  const member = { combatant_id: id, state: { template, active_effect_ids: [] } };
  const attack = template.attacks[0];
  assert.equal(window.IRON_PIT_BROWSER_BARBARIAN2.activate(member, attack, 1), true);
  assert.equal(window.IRON_PIT_BROWSER_BARBARIAN2.attackAdvantage(member.state, attack), 1);
  assert.equal(window.IRON_PIT_BROWSER_BARBARIAN2.attacksAgainstAdvantage(member.state), 1);
}

const winterWolf = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-winter-wolf"];
assert.ok(winterWolf);
assert.ok(winterWolf.traits.includes("pack-tactics"));
assert.ok(winterWolf.source_trait_names.includes("Snow Camouflage"));
assert.equal(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-yeti"], undefined,
  "Yeti must remain fail-closed until Fear of Fire is modeled");

console.log("2014 Reckless and flat-arena trait browser parity passed.");
