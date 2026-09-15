const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = {};
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: (member, max) => ({ tiny: 0, small: 1, medium: 2 }[member.state.template.size] <= ({ tiny: 0, small: 1, medium: 2 }[max])) };
window.IRON_PIT_BROWSER_GRAPPLE = { release: (state, sourceId) => { state.grapple_sources = state.grapple_sources.filter((item) => item.source_id !== sourceId); } };
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, round, actor, target, attack) => ({
    sequence, round_number: round, hit: true, actor_id: actor.combatant_id, target_id: target.combatant_id,
    applied_condition_ids: [], feature_id: null, description: `${attack.name} hits.`,
  }),
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp = Math.max(0, state.current_hp - amount); },
};
window.IRON_PIT_DICE = { rollMany: (count) => Array.from({ length: count }, () => 2) };
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-swallow.js"), "utf8"), { filename: "browser-swallow.js" });

const frog = {
  combatant_id: "frog", side: "monsters", state: {
    template: { name: "Giant Frog", attacks: [{ id: "bite", name: "Bite" }], swallowAction: {
      id: "swallow", attackId: "bite", maxTargetSize: "small", maxSwallowed: 1,
      damageDiceCount: 2, damageDiceSize: 4, damageBonus: 0, damageType: "acid", exitProne: true,
    } }, current_hp: 18, is_alive: true, is_dead: false, swallowed: null, grapple_sources: [], active_effect_ids: [],
  },
};
const hero = {
  combatant_id: "hero", side: "heroes", state: {
    template: { name: "Hero", size: "small" }, current_hp: 20, is_alive: true, is_dead: false,
    swallowed: null, grapple_sources: [{ source_id: "frog" }], active_effect_ids: [],
  },
};
const setup = { heroes: [hero], monsters: [frog] };
const W = window.IRON_PIT_BROWSER_SWALLOW;
assert.equal(W.target(frog, setup), hero);
const result = W.resolve(1, 1, frog, setup);
assert.equal(result.events[0].feature_id, "swallow");
assert.equal(hero.state.swallowed.source_id, "frog");
assert.deepEqual(hero.state.grapple_sources, []);
const damage = W.startTurn(result.sequence, 2, frog, setup);
assert.equal(hero.state.current_hp, 16);
frog.state.is_alive = false; frog.state.is_dead = true;
W.cleanup(setup);
assert.equal(hero.state.swallowed, null);
assert.ok(hero.state.active_effect_ids.includes("prone"));
console.log("browser swallow regression passed");
