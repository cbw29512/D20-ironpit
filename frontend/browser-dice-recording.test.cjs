"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const values = [16, 3, 5];
const context = {
  console,
  crypto: {
    getRandomValues(buffer) {
      assert.ok(values.length, "test entropy exhausted");
      buffer[0] = values.shift();
      return buffer;
    },
  },
};
context.window = context;
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname, "browser-dice.js"), "utf8"), context, { filename: "browser-dice.js" });

const dice = context.IRON_PIT_DICE;
assert.equal(dice.roll(20), 17);
assert.deepEqual(Array.from(dice.rollMany(2, 6)), [4, 6]);
assert.deepEqual(JSON.parse(JSON.stringify(dice.getHistory())), [
  { sides: 20, value: 17 }, { sides: 6, value: 4 }, { sides: 6, value: 6 },
]);
const copy = dice.getHistory(); copy[0].value = 1;
assert.equal(dice.getHistory()[0].value, 17, "diagnostic callers must not mutate production roll history");
dice.clearHistory(); assert.deepEqual(JSON.parse(JSON.stringify(dice.getHistory())), []);
assert.equal(values.length, 0, "every production roll must come from Web Crypto entropy");

console.log("production secure dice recording regression passed");
