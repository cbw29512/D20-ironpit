const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = global;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-monsters-2014.js");
load("browser-terminal-effects.js");

const roster = Object.values(window.IRON_PIT_BROWSER_MONSTERS_2014);
const armor = roster.find((item) => item.name === "Animated Armor");
const sword = roster.find((item) => item.name === "Flying Sword");

for (const template of [armor, sword]) {
  assert.ok(template, "Antimagic-only construct must be in the certified 2014 browser roster");
  assert.deepEqual(template.terminal_effect_tags, ["antimagic"]);
  const state = {
    template,
    current_hp: template.max_hp,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    is_stable: false,
    active_effect_ids: ["dodge"],
    concentration: null,
  };
  assert.equal(window.IRON_PIT_BROWSER_TERMINAL_EFFECTS.applyTerminalEffectTag(state, "antimagic"), "dead");
  assert.equal(state.current_hp, 0);
  assert.equal(state.is_alive, false);
  assert.equal(state.is_dead, true);
  assert.equal(state.is_unconscious, false);
  assert.equal(state.is_stable, false);
  assert.equal(state.active_effect_ids.includes("dodge"), false);
}

{
  const state = {
    template: armor,
    current_hp: armor.max_hp,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    is_stable: false,
    active_effect_ids: [],
    concentration: null,
  };
  assert.equal(window.IRON_PIT_BROWSER_TERMINAL_EFFECTS.applyTerminalEffectTag(state, "fire"), "not_susceptible");
  assert.equal(state.current_hp, armor.max_hp);
  assert.equal(state.is_dead, false);
}

console.log("2014 Antimagic Susceptibility terminal semantics passed.");
