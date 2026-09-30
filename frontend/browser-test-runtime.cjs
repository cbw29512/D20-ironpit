"use strict";

const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// Load the website's module order so standalone fixtures cannot hide missing dependencies.
function loadWebsite(page = "frontend/index.html") {
  try {
    global.window = globalThis;
    const root = path.resolve(__dirname, "..");
    const html = fs.readFileSync(path.join(root, page), "utf8");
    for (const [, file] of html.matchAll(/<script[^>]*src="([^"]+)"/g)) {
      if (!file.startsWith("browser-")) continue;
      vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
      if (file === "browser-engine.js") break;
    }
    // The actual UI loads this bundle lazily when selecting the 2014 lane.
    vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-monsters-2014.js"), "utf8"), {
      filename: "browser-monsters-2014.js",
    });
  } catch (error) {
    console.error("Website runtime fixture failed to initialize.", page, error);
    throw error;
  }
}

module.exports = { loadWebsite };
