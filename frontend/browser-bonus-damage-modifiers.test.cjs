"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

let rolls = [];
window.IRON_PIT_DICE = {
  roll: (sides) => {
    const value = rolls.shift();
    if (!Number.isInteger(value) || value < 1 || value > sides) throw new Error("Invalid fixed die.");
    return value;
  },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    return "damaged";
  },
};

load("browser-modifiers.js");
load("browser-rolls.js");
load("browser-hit-damage.js");

function attacker() {
  return {
    template: { name: "Attacker", traits: [], brutal_critical_dice: 0 },
    active_modifiers: [],
    feature_last_turn_keys: {},
  };
}

function defender() {
  return {
    template: { name: "Defender", max_hp: 100 },
    current_hp: 100,
    temporary_hp: 0,
    active_modifiers: [],
  };
}

const attack = {
  id: "sword",
  name: "Sword",
  kind: "melee",
  diceCount: 1,
  diceSize: 8,
  damageBonus: 3,
  damageType: "slashing",
  onHitDamage: [],
};

{
  const source = attacker();
  window.IRON_PIT_BROWSER_MODIFIERS.add(source, {
    id: "caster:divine-favor:self:0",
    source_id: "caster",
    source_effect_id: "divine-favor",
    source_name: "Divine Favor",
    source_is_magical: true,
    kind: "bonus-damage",
    dice_count: 1,
    dice_size: 4,
    damage_type: "radiant",
    target_id: null,
  });
  const target = defender();
  rolls = [5, 4];

  const result = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
    source, target, attack, false, "normal", "1:attacker",
    { targetId: "target-1", affectedStates: [source, target] },
  );

  const rider = result.damageComponents.find((item) => item.source === "Divine Favor");
  assert.ok(rider);
  assert.equal(rider.notation, "1d4+0");
  assert.deepEqual(rider.rolls, [4]);
  assert.equal(rider.damage_type, "radiant");
}

{
  const source = attacker();
  window.IRON_PIT_BROWSER_MODIFIERS.add(source, {
    id: "caster:marked:rider:0",
    source_id: "caster",
    source_effect_id: "marked-rider",
    source_name: "Marked Rider",
    kind: "bonus-damage",
    dice_count: 1,
    dice_size: 4,
    damage_type: "radiant",
    target_id: "target-2",
  });

  rolls = [5];
  const wrong = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
    source, defender(), attack, false, "normal", "1:attacker",
    { targetId: "target-1" },
  );
  assert.equal(wrong.damageComponents.some((item) => item.source === "Marked Rider"), false);

  rolls = [5, 3];
  const right = window.IRON_PIT_BROWSER_HIT_DAMAGE.resolve(
    source, defender(), attack, false, "normal", "1:attacker",
    { targetId: "target-2" },
  );
  assert.equal(right.damageComponents.some((item) => item.source === "Marked Rider"), true);
}

console.log("Universal browser bonus-damage modifier parity passed.");
