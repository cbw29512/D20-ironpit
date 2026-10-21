"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;
vm.runInThisContext(fs.readFileSync(require("node:path").join(__dirname, "browser-death-trigger-rules.js"), "utf8"));
const rules = window.IRON_PIT_BROWSER_DEATH_TRIGGER_RULES;
const hero = { is_dead: false, current_hp: 0, death_save_failures: 2,
  active_buff_effect_ids: ["death-trigger"], feature_use_counts: {} };
assert.equal(rules.consume(hero), false);
hero.is_dead = true;
hero.death_save_failures = 3;
assert.equal(rules.consume(hero), true);
assert.equal(rules.consume(hero), false);
const monster = { is_dead: true, current_hp: 0, active_buff_effect_ids: ["death-trigger"], feature_use_counts: {} };
assert.equal(rules.consume(monster), true);
assert.equal(rules.consume({ ...monster, active_buff_effect_ids: [] }), false);
console.log("Browser actual-death trigger gate verified");
