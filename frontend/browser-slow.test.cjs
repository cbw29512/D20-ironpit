"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  if (!fs.existsSync(htmlPath)) continue;
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /browser-slow\.js/, `${htmlPath} must load Slow mastery`);
  assert.ok(html.indexOf("browser-weapon-mastery.js") < html.indexOf("browser-slow.js"));
  assert.ok(html.indexOf("browser-slow.js") < html.indexOf("browser-attack.js"));
}
for (const file of [
  "browser-modifier-validation.js", "browser-modifiers.js", "browser-weapon-mastery.js",
  "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-slow.js",
]) load(file);

const attacker = { template: { weapon_masteries: ["longbow"] } };
const attack = { id: "rowan-2024-longbow", weaponId: "longbow", masteryProperty: "Slow" };
const target = { current_hp: 12, is_dead: false, template: { id: "target" }, active_modifiers: [] };
assert.equal(window.IRON_PIT_BROWSER_SLOW.active(attacker, attack), true);
assert.equal(window.IRON_PIT_BROWSER_SLOW.apply(attacker, "rowan", target, attack), true);
assert.equal(target.active_modifiers[0].kind, "speed");
assert.equal(target.active_modifiers[0].flat_bonus, -10);
assert.equal(target.active_modifiers[0].expires_at_start_of_source_turn, true);
