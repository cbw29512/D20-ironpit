const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
vm.runInThisContext(fs.readFileSync(require.resolve("./browser-attack-advantage.js"), "utf8"), { filename: "browser-attack-advantage.js" });
const attack = { conditionalAttackAdvantage: [{ trigger: "target_not_full_hp" }] };
const target = (hp, bonus = 0) => ({ current_hp: hp, max_hp_bonus: bonus, grapple_sources: [], template: { max_hp: 20 } });
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(attack, target(20)), 0);
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(attack, target(19)), 1);
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(attack, target(25, 5)), 0);
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(attack, target(24, 5)), 1);

const grappleAttack = { conditionalAttackAdvantage: [{ trigger: "target_grappled_by_source" }] };
const grappled = target(20);
grappled.grapple_sources.push({ source_id: "ankheg-1" });
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(grappleAttack, grappled, "ankheg-1"), 1);
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(grappleAttack, grappled, "other-1"), 0);
assert.throws(() => window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources(grappleAttack, grappled));
assert.throws(() => window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE.sources({ conditionalAttackAdvantage: [{ trigger: "bad" }] }, target(19)));
console.log("Browser conditional attack Advantage regressions passed.");
