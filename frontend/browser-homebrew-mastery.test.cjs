"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-weapon-mastery.js"), "utf8"),
  { filename: "browser-weapon-mastery.js" },
);

const mastery = window.IRON_PIT_BROWSER_WEAPON_MASTERY;
const greatsword = {
  id: "homebrew-greatsword",
  name: "Greatsword",
  kind: "melee",
  weaponId: "greatsword",
  masteryProperty: "Graze",
};

function state({ kind = "monster", ruleset = "2024", owned = true, mastered = true } = {}) {
  return {
    template: {
      kind,
      ruleset,
      attacks: owned ? [{ ...greatsword }] : [],
      weapon_masteries: mastered ? ["greatsword"] : [],
    },
  };
}

assert.equal(
  mastery.active(state({ kind: "monster" }), greatsword, "Graze"),
  true,
  "an explicitly equipped 2024 homebrew monster gets the same mastery as a pregen",
);
assert.equal(
  mastery.active(state({ kind: "character" }), greatsword, "Graze"),
  true,
  "actor kind must not change the mastery contract",
);
assert.equal(
  mastery.active(state({ mastered: false }), greatsword, "Graze"),
  false,
  "owning a weapon alone must not grant mastery",
);
assert.equal(
  mastery.active(state({ owned: false }), greatsword, "Graze"),
  false,
  "selecting mastery for an unowned weapon must not activate it",
);
assert.equal(
  mastery.active(state({ ruleset: "2014" }), greatsword, "Graze"),
  false,
  "2014 combatants must not activate the 2024 mastery layer",
);
assert.equal(
  mastery.active(state(), greatsword, "Topple"),
  false,
  "the requested mastery must match the weapon's configured mastery property",
);

console.log("Browser homebrew weapon-mastery contract passed.");
