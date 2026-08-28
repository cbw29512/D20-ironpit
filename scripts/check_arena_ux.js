"use strict";

const fs = require("fs");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

try {
  const html = fs.readFileSync("frontend/index.html", "utf8");
  const app = fs.readFileSync("frontend/app.js", "utf8");
  const arenaView = fs.readFileSync("frontend/arena-view.js", "utf8");
  const figures = fs.readFileSync("frontend/figure-view.js", "utf8");

  const buttons = html.match(/<button\b/g) || [];
  assert(buttons.length === 1, "Public arena must expose exactly one button.");
  assert(html.includes('id="fight-button"'), "Public arena must expose the Fight button.");
  assert(!html.includes("ranged-button"), "Public arena must not expose a ranged-mode button.");
  assert(!html.includes("rogue-button"), "Public arena must not expose an ambush-mode button.");
  assert(html.includes("https://buymeacoffee.com/divclass016"), "Buy Me a Coffee support URL must remain present.");
  assert(html.includes("☕ Buy Me a Coffee"), "Support CTA must be plainly labeled Buy Me a Coffee.");
  assert(app.includes("buildAutomaticBattle"), "Browser preview must use monster-driven automatic battle selection.");
  assert(app.includes("/api/test/fight/"), "Live API path must use the one-button fight endpoint.");
  assert(!arenaView.includes("scrollIntoView"), "Battle log must not scroll the whole page.");
  assert(arenaView.includes("log.scrollTop = log.scrollHeight"), "Battle log must scroll internally.");
  for (const key of ["fighter", "rogue", "goblin", "bandit", "guard"]) {
    assert(figures.includes(`${key}:`), `Representative ${key} figure must remain available.`);
  }
  for (const cue of ["sword", "bow", "scimitar", "spear"]) {
    assert(figures.includes(cue), `Figure renderer must retain a recognizable ${cue} cue.`);
  }

  console.log("Arena UX checks passed.");
} catch (error) {
  console.error("Arena UX checks failed", error);
  process.exitCode = 1;
}
