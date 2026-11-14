"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

// Data contract: six immutable selected cards per side, no extra combat slots.
// Display mapping: indexes 0..2 melee, indexes 3..5 ranged.
try {
  const css = fs.readFileSync(path.join(__dirname, "player-six-v-six.css"), "utf8");
  const app = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
  const view = fs.readFileSync(path.join(__dirname, "battlefield-view.js"), "utf8");
  assert.match(app, /const MAX_SLOTS = 6;/);
  assert.match(view, /const MAX_SLOTS = 6;/);
  assert.match(css, /grid-template-columns:\s*minmax\(0,1fr\)\s+minmax\(136px,174px\)\s+minmax\(0,1fr\)/,
    "Both teams must flank one central controls column.");
  assert.match(css, /grid-template-rows:\s*repeat\(3,minmax\(0,1fr\)\)/,
    "Three paired rows show six combatants per side.");
  const placement = (side, index, col, row) => {
    const rx = new RegExp("#" + side + "-slots > :nth-child\\(" + index +
      "\\) \\{ grid-area: " + row + " / " + col + "; \\}");
    assert.match(css, rx, "Wrong " + side + " slot " + index + " position.");
  };
  for (let row = 1; row <= 3; row++) {
    placement("hero", row, 2, row);
    placement("hero", row + 3, 1, row);
    placement("monster", row, 1, row);
    placement("monster", row + 3, 2, row);
  }
  for (const pageName of ["index.html", "frontend/index.html"]) {
    const html = fs.readFileSync(path.join(__dirname, "..", pageName), "utf8");
    assert.equal((html.match(/id="fight-button"/g) || []).length, 1,
      pageName + " must contain only one fight-start button.");
    assert.equal((html.match(/class="lane-headers"/g) || []).length, 2,
      pageName + " requires two mirrored lane legends.");
    assert.match(html, /<span>RANGED<\/span><span>MELEE<\/span><\/div><div id="hero-slots"/);
    assert.match(html, /<span>MELEE<\/span><span>RANGED<\/span><\/div><div id="monster-slots"/);
    for (const [id, side] of [["hero-slots", "heroes"], ["monster-slots", "monsters"]]) {
      const anchor = html.indexOf('id="' + id + '"');
      assert.ok(anchor !== -1, "Missing " + id);
      const segment = html.slice(anchor, html.indexOf("</div></div>", anchor));
      assert.equal((segment.match(new RegExp('class="battle-card empty-slot ' + side + '"', "g")) || []).length,
        6, pageName + " must offer exactly six initial combatant slots for " + side);
    }
    assert.ok(html.indexOf('href="player-six-v-six.css"') >
      html.indexOf('href="bulk-combat.css"'), "Mirrored formation must override legacy board styles.");
  }
  console.log("Mirrored 6v6: 3 ranged + 3 melee per team, one Fight button, no engine edits.");
} catch (error) {
  console.error("Mirrored battlefield layout regression failed", error);
  process.exitCode = 1;
}