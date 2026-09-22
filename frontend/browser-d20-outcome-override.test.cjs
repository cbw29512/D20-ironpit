"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-d20-outcome-override.js"), "utf8"),
  { filename: "browser-d20-outcome-override.js" },
);

const O = window.IRON_PIT_BROWSER_D20_OVERRIDE;
function state(uses = 1) {
  return {
    template: { failed_d20_to_natural_20_resource_id: "stroke-of-luck" },
    resources: { "stroke-of-luck": uses },
  };
}

{
  const actor = state();
  const original = {
    notation: "2d20kh1",
    rolls: [2, 15],
    selected_roll: 15,
    modifier: 3,
    total: 18,
    revisions: [],
  };
  const result = O.apply(actor, original, 19);
  assert.equal(result.used, true);
  assert.equal(result.roll.selected_roll, 20);
  assert.equal(result.roll.total, 23);
  assert.deepEqual(result.roll.rolls, [2, 15], "Stroke overrides the accepted result, not the raw dice");
  assert.equal(result.roll.revisions[0].kind, "selected_result_override");
  assert.deepEqual(result.roll.revisions[0].replacement_rolls, [2, 15]);
  assert.equal(actor.resources["stroke-of-luck"], 0);
}

{
  const actor = state();
  const successful = {
    notation: "1d20",
    rolls: [18],
    selected_roll: 18,
    modifier: 5,
    total: 23,
    revisions: [],
  };
  const result = O.apply(actor, successful, 20);
  assert.equal(result.used, false);
  assert.equal(actor.resources["stroke-of-luck"], 1);
}

{
  const actor = state(0);
  const failed = {
    notation: "1d20",
    rolls: [1],
    selected_roll: 1,
    modifier: 5,
    total: 6,
    revisions: [],
  };
  const result = O.apply(actor, failed, 20);
  assert.equal(result.used, false);
  assert.equal(result.roll.selected_roll, 1);
}

for (const htmlName of ["index.html", path.join("..", "index.html")]) {
  const html = fs.readFileSync(path.join(__dirname, htmlName), "utf8");
  assert.match(html, /browser-d20-outcome-override\.js/);
  assert.match(html, /browser-attack-post-roll\.js/);
  assert.ok(
    html.indexOf("browser-d20-outcome-override.js") < html.indexOf("browser-attack-post-roll.js"),
    "D20 result override must load before post-roll attack sequencing",
  );
  assert.ok(
    html.indexOf("browser-attack-post-roll.js") < html.indexOf("browser-attack.js"),
    "post-roll sequencing must load before attack resolution",
  );
  assert.ok(
    html.indexOf("browser-d20-outcome-override.js") < html.indexOf("browser-saves.js"),
    "D20 result override must load before saving throw resolution",
  );
}

console.log("Browser generic D20 result-override regressions passed.");
