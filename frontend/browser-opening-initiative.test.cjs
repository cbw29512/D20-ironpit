const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {
  IRON_PIT_DICE: {
    roll: () => 3,
    rollMany: (count) => Array(count).fill(3),
  },
};
vm.runInThisContext(fs.readFileSync(require.resolve("./browser-rolls.js"), "utf8"), { filename: "browser-rolls.js" });
vm.runInThisContext(fs.readFileSync(require.resolve("./browser-attack-advantage.js"), "utf8"), { filename: "browser-attack-advantage.js" });

const attacker = { initiative_total: 18, current_hp: 10, feature_last_turn_keys: {}, template: { max_hp: 10, traits: [] } };
const target = { initiative_total: 12, current_hp: 10, active_effect_ids: [], template: { max_hp: 10 } };
const attack = {
  name: "Test attack", kind: "melee", diceCount: 1, diceSize: 6, damageBonus: 0, damageType: "piercing",
  conditionalDamage: { trigger: "round1_initiative_lead", mode: "add", diceCount: 2, diceSize: 6, damageBonus: 0, damageType: "piercing" },
};

const opening = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(attacker, attack, false, "normal", "1:attacker", null, target);
assert.equal(opening.components.length, 2);
assert.equal(opening.components[1].source, "Opening initiative bonus damage");

const later = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(attacker, attack, false, "normal", "2:attacker", null, target);
assert.equal(later.components.length, 1);

target.initiative_total = 18;
const tie = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(attacker, attack, false, "normal", "1:attacker", null, target);
assert.equal(tie.components.length, 1);

target.initiative_total = 12;
attacker.template.traits = ["assassinate"];
const assassinate = window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE;
assert.equal(assassinate.sources({ conditionalAttackAdvantage: [] }, target, "attacker", attacker, 1), 1);
assert.equal(assassinate.sources({ conditionalAttackAdvantage: [] }, target, "attacker", attacker, 2), 0);
target.active_effect_ids.push("surprised");
assert.equal(assassinate.assassinateCritical(attacker, target), true);
console.log("Browser opening initiative and Assassinate regressions passed.");
