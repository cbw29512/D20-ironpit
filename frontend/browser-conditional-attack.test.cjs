"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-conditional-attack.js");

const attack = {
  id: "test-bite",
  conditionalAttackModifiers: [{ trigger: "target_missing_hp", mode: "advantage" }],
};
const attacker = { current_hp: 10, template: { max_hp: 10 } };
const defender = { current_hp: 20, template: { max_hp: 20 } };

assert.equal(window.IRON_PIT_BROWSER_CONDITIONAL_ATTACK.advantage(attacker, defender, attack), 0);
assert.equal(window.IRON_PIT_BROWSER_CONDITIONAL_ATTACK.disadvantage(attacker, defender, attack), 0);
defender.current_hp = 19;
assert.equal(window.IRON_PIT_BROWSER_CONDITIONAL_ATTACK.advantage(attacker, defender, attack), 1);
assert.equal(window.IRON_PIT_BROWSER_CONDITIONAL_ATTACK.disadvantage(attacker, defender, attack), 0);

for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /browser-conditional-attack\.js/, `${htmlPath} must load conditional attack rules`);
  assert.ok(html.indexOf("browser-conditional-attack.js") < html.indexOf("browser-attack.js"));
}

console.log("Browser target-missing-hp conditional attack modifiers and production wiring passed.");
