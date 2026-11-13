"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

try {
  const read = file => fs.readFileSync(path.join(__dirname, file), "utf8");
  const source = read("index.html");
  const lab = read("engine-test-lab.html");
  const scripts = html => [...html.matchAll(/<script defer src="([^"]+)"><\/script>/g)]
    .map(match => match[1]);
  const engineScripts = html => {
    const list = scripts(html);
    const start = list.indexOf("browser-dice.js");
    const end = list.indexOf("browser-engine.js");
    assert.ok(start >= 0 && end > start, "Missing shared engine script markers.");
    return list.slice(start, end + 1);
  };
  assert.deepEqual(engineScripts(lab), engineScripts(source),
    "The Test All page must load the exact player combat engine modules in order.");
  const all = scripts(lab);
  for (const file of [
    "browser-formation-engagement.js", "browser-formation-area-targeting.js",
    "browser-death-trigger-dispatch.js", "browser-breakable-condition-object.js",
    "browser-target-chosen-save.js", "engine-test-lab-sweep-report.js",
    "engine-test-lab-sweep-runner.js", "engine-test-lab-sweep-ui.js",
  ]) assert.equal(all.filter(value => value === file).length, 1,
    "Required Test All script missing or duplicated: " + file);
  assert.ok(all.indexOf("engine-test-lab-sweep-report.js") <
    all.indexOf("engine-test-lab-sweep-runner.js"),
  "Bounded report must load before the sweep runner.");
  assert.match(lab, /id="sweep-start"/);
  assert.match(lab, /id="sweep-download"/);
  console.log("Iron Pit player/Test All engine script parity and resume UI passed.");
} catch (error) {
  console.error("Iron Pit Test All engine parity regression failed", error);
  process.exitCode = 1;
}
