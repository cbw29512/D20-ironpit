"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /<script src="browser-sneak-attack\.js"><\/script>/, `${htmlPath} must load shared Rogue Sneak Attack rules`);
  assert.ok(html.indexOf("browser-sneak-attack.js") < html.indexOf("browser-rolls.js"), "Sneak Attack must load before damage rolls");
}

load("browser-sneak-attack.js");
load("browser-rolls.js");

function rogue(dice = 1) {
  return { template: { sneak_attack_d6: dice, traits: [] }, feature_last_turn_keys: {} };
}

const attack = {
  id: "test-shortsword", name: "Shortsword", kind: "melee", diceCount: 1, diceSize: 6,
  damageBonus: 3, damageType: "piercing", sneakAttackEligible: true,
};
const ineligible = { ...attack, id: "test-club", name: "Club", sneakAttackEligible: false };

{
  const state = rogue();
  assert.equal(window.IRON_PIT_BROWSER_SNEAK_ATTACK.bonusDamage(state, attack, "normal", "1:rogue", false), null);
  assert.equal(window.IRON_PIT_BROWSER_SNEAK_ATTACK.bonusDamage(state, attack, "disadvantage", "1:rogue", true), null);
  assert.equal(state.feature_last_turn_keys["sneak-attack"], undefined, "failed eligibility must not consume Sneak Attack");
  assert.equal(window.IRON_PIT_BROWSER_SNEAK_ATTACK.bonusDamage(state, ineligible, "advantage", "1:rogue", true), null);
}

{
  const state = rogue(2);
  const first = window.IRON_PIT_BROWSER_SNEAK_ATTACK.bonusDamage(state, attack, "advantage", "1:rogue", false);
  assert.deepEqual(first, { source: "Sneak Attack", diceCount: 2, diceSize: 6, damageType: "piercing" });
  assert.equal(window.IRON_PIT_BROWSER_SNEAK_ATTACK.bonusDamage(state, attack, "advantage", "1:rogue", false), null,
    "Sneak Attack is once per turn");
  assert.ok(window.IRON_PIT_BROWSER_SNEAK_ATTACK.bonusDamage(state, attack, "normal", "1:enemy", true),
    "a different creature's turn can permit another Sneak Attack");
}

{
  const attacker = { combatant_id: "rogue", side: "heroes", state: rogue() };
  const ally = { combatant_id: "fighter", side: "heroes", state: { is_alive: true, is_dead: false, current_hp: 10, is_unconscious: false } };
  const downAlly = { combatant_id: "cleric", side: "heroes", state: { is_alive: true, is_dead: false, current_hp: 0, is_unconscious: true } };
  assert.equal(window.IRON_PIT_BROWSER_SNEAK_ATTACK.allyAvailable(attacker, { heroes: [attacker, ally], monsters: [] }), true,
    "Iron Pit treats any other active ally as the adjacent-ally Sneak Attack path");
  assert.equal(window.IRON_PIT_BROWSER_SNEAK_ATTACK.allyAvailable(attacker, { heroes: [attacker, downAlly], monsters: [] }), false);
}

{
  const state = rogue();
  const queue = [4, 5, 2, 6];
  window.IRON_PIT_DICE = {
    roll: (sides) => ((queue.shift() ?? 1) - 1) % sides + 1,
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
  const damage = window.IRON_PIT_BROWSER_ROLLS.weaponDamage(state, attack, true, "normal", "2:rogue", null, null, true);
  const sneak = damage.components.find((part) => part.source === "Sneak Attack");
  assert.ok(sneak, "active ally must enable Sneak Attack without Advantage");
  assert.equal(sneak.notation, "2d6+0", "critical hit must double Sneak Attack dice");
  assert.deepEqual(sneak.rolls, [2, 6]);
  assert.equal(damage.components.filter((part) => part.source === "Sneak Attack").length, 1);
}

assert.throws(
  () => window.IRON_PIT_BROWSER_SNEAK_ATTACK.bonusDamage(rogue(), attack, "advantage", null, false),
  /actual active-turn key/,
  "Sneak Attack must fail closed without a real turn identity",
);

console.log("Browser Rogue Sneak Attack regressions passed.");
