"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /browser-topple\.js/, `${htmlPath} must load shared Topple rules`);
  assert.ok(html.indexOf("browser-saves.js") < html.indexOf("browser-topple.js"));
  assert.ok(html.indexOf("browser-topple.js") < html.indexOf("browser-engine.js"));
}
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-sneak-attack.js",
  "browser-rolls.js", "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-weapon-mastery.js",
  "browser-attack.js", "browser-saves.js", "browser-topple.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const toppleAttack = {
  id: "battleaxe-attack", weaponId: "battleaxe", masteryProperty: "Topple", name: "Battleaxe", kind: "melee",
  bonus: 5, diceCount: 1, diceSize: 8, damageBonus: 3, damageType: "slashing", reach: 5,
  animation: "slash", attackAbility: "strength", attackAbilityModifier: 3, onHitDamage: [],
};

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll(sides) { const value = rolls.shift(); if (!(value >= 1 && value <= sides)) throw new Error(`invalid d${sides}: ${value}`); return value; },
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
}
function member(id, side, options = {}) {
  const template = structuredClone(base);
  Object.assign(template, { id: `template-${id}`, name: id, level: options.level ?? 1, armor_class: options.armorClass ?? 10,
    max_hp: 40, attacks: [structuredClone(toppleAttack)], primary_attack_id: toppleAttack.id,
    weapon_masteries: options.mastered === false ? [] : ["battleaxe"], traits: [], size: options.size || "medium",
    condition_immunities: options.immune ? ["prone"] : [], saving_throw_bonuses: { ...template.saving_throw_bonuses, constitution: 0 } });
  if (options.missingModifier) delete template.attacks[0].attackAbilityModifier;
  return { combatant_id: id, side, position_ft: options.position ?? 0, state: S.buildState(template) };
}
function attack(attacker, target, values) {
  dice(values);
  return window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, attacker, target, attacker.state.template.attacks[0], 5, { spendAction: false });
}

{
  const fighter = member("fighter", "heroes"), target = member("target", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4, 5]);
  assert.equal(event.hit, true); assert.equal(event.save_ability, "constitution"); assert.equal(event.save_dc, 13);
  assert.equal(event.save_succeeded, false); assert.equal(event.saving_throw_roll.total, 5);
  assert.ok(event.applied_condition_ids.includes("prone")); assert.ok(target.state.active_effect_ids.includes("prone"));
}

{
  const fighter = member("fighter", "heroes"), target = member("target", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4, 18]);
  assert.equal(event.save_succeeded, true); assert.ok(!target.state.active_effect_ids.includes("prone"));
}

{
  const fighter = member("fighter", "heroes"), target = member("gargantuan", "monsters", { position: 5, size: "gargantuan" });
  const event = attack(fighter, target, [15, 4, 5]);
  assert.equal(event.save_succeeded, false, "Topple has no target-size restriction"); assert.ok(target.state.active_effect_ids.includes("prone"));
}

{
  const fighter = member("fighter", "heroes", { mastered: false }), target = member("target", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4]);
  assert.equal(event.save_dc, null); assert.equal(event.saving_throw_roll, null); assert.ok(!target.state.active_effect_ids.includes("prone"));
}

{
  const fighter = member("fighter", "heroes"), immune = member("immune", "monsters", { position: 5, immune: true });
  const prone = member("prone", "monsters", { position: 5 }); prone.state.active_effect_ids.push("prone");
  assert.equal(attack(fighter, immune, [15, 4]).save_dc, null);
  assert.equal(attack(member("fighter2", "heroes"), prone, [15, 4]).save_dc, null);
}

{
  const fighter = member("fighter", "heroes", { level: 5 }), target = member("target", "monsters", { position: 5 });
  const event = attack(fighter, target, [15, 4, 13]);
  assert.equal(event.save_dc, 14); assert.equal(event.save_succeeded, false);
}

{
  const fighter = member("fighter", "heroes", { missingModifier: true }), target = member("target", "monsters", { position: 5 });
  assert.throws(() => attack(fighter, target, [15, 4]), /explicit attack ability modifier/);
}

console.log("Browser Topple weapon mastery regressions passed.");
