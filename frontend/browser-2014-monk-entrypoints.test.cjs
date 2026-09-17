"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

function read(relativePath) {
  try {
    return fs.readFileSync(path.join(__dirname, relativePath), "utf8");
  } catch (error) {
    console.error("Failed to read Iron Pit entrypoint", { relativePath, error });
    throw error;
  }
}

try {
  const frontend = read("index.html");
  const root = read(path.join("..", "index.html"));
  const moduleName = "browser-2014-monk.js";
  assert.ok(frontend.includes(moduleName), "frontend/index.html must load the 2014 Monk runtime");
  assert.ok(root.includes(moduleName), "root index.html must load the 2014 Monk runtime");
  console.log("Both Iron Pit entrypoints load the 2014 Monk browser runtime.");
} catch (error) {
  console.error("2014 Monk entrypoint certification failed", { error });
  process.exitCode = 1;
}
