"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /browser-weapon-mastery\.js/, `${htmlPath} must load universal mastery rules`);
  assert.match(html, /browser-graze\.js/, `${htmlPath} must load shared Graze rules`);
  assert.ok(html.indexOf("browser-weapon-mastery.js") < html.indexOf("browser-graze.js"));
  assert.ok(html.indexOf("browser-graze.js") < html.indexOf("browser-attack.js"));
}
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-sneak-attack.js",
  "browser-rolls.js", "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-weapon-mastery.js",
  "browser-graze.js", "browser-attack.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const grazeAttack = {
  id: "graze-greatsword", weaponId: "greatsword", masteryProperty: "Graze", name: "Greatsword", kind: "melee",
  bonus: 5, diceCount: 2, diceSize: 6, damageBonus: 99, damageType: "slashing", reach: 5,
  animation: "heavy-slash", attackAbility: "strength", attackAbilityModifier: 3, onHitDamage: [],
};

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll(sides) {
      const value = rolls.shift();
      if (!(value >= 1 && value <= sides)) throw new Error(`invalid d${sides}: ${value}`);
      return value;
    },
    rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
  };
}

function member(id, side, options = {}) {
  const template = structuredClone(base);
  const attack = { ...grazeAttack, attackAbilityModifier: options.modifier ?? 3 };
  if (options.missingModifier) delete attack.attackAbilityModifier;
  Object.assign(template, {
    id: `template-${id}`, name: id, armor_class: options.armorClass ?? 30,
    attacks: [attack], primary_attack_id: attack.id,
    weapon_masteries: options.mastered === false ? [] : ["greatsword"], traits: [],
    damage_resistances: options.resistant ? ["slashing"] : [],
    damage_vulnerabilities: options.vulnerable ? ["slashing"] : [],
    damage_immunities: options.immune ? ["slashing"] : [],
  });
  return { combatant_id: id, side, position_ft: side === "heroes" ? 0 : 5, state: S.buildState(template) };
}

function miss(attacker, target) {
  dice([1]);
  return window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
    1, 1, attacker, target, attacker.state.template.attacks[0], 5, { spendAction: false },
  );
}

{
  const fighter = member("fighter", "heroes"), target = member("target", "monsters");
  const before = target.state.current_hp;
  const event = miss(fighter, target);
  assert.equal(event.hit, false);
  assert.equal(event.damage_roll.total, 3, "Graze uses the attack ability modifier, not damageBonus 99");
  assert.equal(event.damage_components[0].source, "Greatsword (Graze)");
  assert.equal(event.damage_components[0].damage_type, "slashing");
  assert.equal(target.state.current_hp, before - 3);
  assert.match(event.description, /Graze deals 3 slashing damage/);
}

{
  const fighter = member("fighter", "heroes", { mastered: false }), target = member("target", "monsters");
  const before = target.state.current_hp;
  const event = miss(fighter, target);
  assert.equal(event.damage_roll, null);
  assert.deepEqual(event.damage_components, []);
  assert.equal(target.state.current_hp, before);
}

{
  const fighter = member("fighter", "heroes");
  const resistant = member("resistant", "monsters", { resistant: true });
  const vulnerable = member("vulnerable", "monsters", { vulnerable: true });
  assert.equal(miss(fighter, resistant).damage_roll.total, 1);
  assert.equal(miss(fighter, vulnerable).damage_roll.total, 3, "Vulnerability cannot increase strict Graze damage");
}

{
  const fighter = member("fighter", "heroes"), immune = member("immune", "monsters", { immune: true });
  const before = immune.state.current_hp;
  const event = miss(fighter, immune);
  assert.equal(event.damage_roll.total, 0);
  assert.equal(event.damage_components[0].applied_total, 0);
  assert.equal(immune.state.current_hp, before);
}

{
  const fighter = member("fighter", "heroes", { modifier: -2 }), target = member("target", "monsters");
  assert.equal(miss(fighter, target).damage_roll.total, 0, "damage cannot fall below zero");
}

{
  const fighter = member("fighter", "heroes", { missingModifier: true }), target = member("target", "monsters");
  assert.throws(() => miss(fighter, target), /requires an explicit attack ability modifier/);
}

console.log("Browser Graze weapon mastery regressions passed.");
