const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
vm.runInThisContext(fs.readFileSync(require.resolve("./browser-attack-advantage.js"), "utf8"), { filename: "browser-attack-advantage.js" });
const attack = { conditionalAttackAdvantage: [{ trigger: "round1_initiative_lead" }] };
const attacker = { initiative_total: 18 };
const target = { initiative_total: 12, current_hp: 20, max_hp_bonus: 0, max_hp_reduction: 0, grapple_sources: [], template: { max_hp: 20 } };
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(attack, target, null, attacker, 1), 1);
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(attack, target, null, attacker, 2), 0);
target.initiative_total = 18;
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(attack, target, null, attacker, 1), 0);
console.log("Browser Ambusher initiative regressions passed.");
