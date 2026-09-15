const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

function load(file) {
  vm.runInThisContext(fs.readFileSync(require.resolve(file), "utf8"), { filename: file });
}

global.window = {
  IRON_PIT_BROWSER_DAMAGE_ABSORPTION: { matches: () => false, apply: () => 0 },
  IRON_PIT_BROWSER_CONDITION_RULES: {
    attackAdvantage: () => false,
    autoCritical: () => false,
    has: () => false,
    incapacitated: () => false,
  },
};

load("./browser-monsters-generated.js");
load("./browser-attack.js");

const fleshGolem = window.IRON_PIT_BROWSER_MONSTERS["2014-flesh-golem"];
assert.ok(fleshGolem, "Flesh Golem must be present in the certified 2014 browser roster");
assert.deepEqual(fleshGolem.conditional_damage_immunities, [{
  damageTypes: ["bludgeoning", "piercing", "slashing"],
  nonmagicalAttackOnly: true,
  bypassIfSilvered: false,
  bypassIfAdamantine: true,
}]);

const target = {
  template: fleshGolem,
  temporary_damage_resistances: [],
  active_effect_ids: [],
};
const mundaneCrossbow = { damageType: "piercing", magical: false, adamantine: false, silvered: false };
const adamantineSword = { damageType: "slashing", magical: false, adamantine: true, silvered: false };
const magicSword = { damageType: "slashing", magical: true, adamantine: false, silvered: false };

assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(target, 10, "piercing", true, false, mundaneCrossbow), 0,
  "mundane physical weapon damage must be immune");
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(target, 10, "slashing", true, false, adamantineSword), 10,
  "adamantine weapon must bypass Flesh Golem immunity");
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(target, 10, "slashing", true, false, magicSword), 10,
  "magical weapon must bypass nonmagical-attack immunity");
assert.equal(window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(target, 10, "bludgeoning", true, false, null), 10,
  "qualified weapon immunity must not block physical damage with no weapon attack context");

console.log("Browser 2014 qualified weapon defense regression passed.");