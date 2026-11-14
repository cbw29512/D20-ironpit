"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {TextEncoder} = require("node:util");

(async () => {
  try {
    const files = new Map(), responses = [];
    let flushCount = 0, closeCount = 0;
    const root = {
      async getFileHandle(name, options) {
        assert.equal(options.create, true);
        if (!files.has(name)) files.set(name, {bytes: []});
        const file = files.get(name);
        return {async createSyncAccessHandle() { return {
          truncate(size) { assert.equal(size, 0); file.bytes = []; },
          write(chunk, {at}) {
            assert.equal(at, file.bytes.length);
            // Force partial writes to prove byte offsets are handled safely.
            const len = Math.min(chunk.length, 3);
            file.bytes.push(...chunk.subarray(0, len));
            return len;
          },
          flush() { flushCount++; },
          close() { closeCount++; },
        }; }};
      },
    };
    const self = {postMessage: response => responses.push(response)};
    const context = {console, self, TextEncoder,
      navigator: {storage: {async getDirectory() { return root; }}}};
    const source = fs.readFileSync(path.join(__dirname,
      "bulk-combat-log-worker.js"), "utf8");
    vm.runInNewContext(source, context, {filename: "bulk-combat-log-worker.js"});
    let serial = 0;
    const send = async (action, extra = {}) => {
      const id = ++serial;
      await self.onmessage({data: {id, action, ...extra}});
      const response = responses.pop();
      assert.equal(response.id, id);
      return response;
    };
    const name = "iron-pit-bag-complete-12345-123456789.txt";
    assert.equal((await send("start", {name})).ok, true);
    const logLine = "ROUND 1 — Hero strikes Bag\n";
    assert.equal((await send("append", {text: logLine})).ok, true);
    for (let i = 1; i < 20; i++)
      assert.equal((await send("append", {text: "EVENT\n"})).ok, true);
    assert.ok(flushCount >= 1, "Every 20 writes must checkpoint to disk");
    assert.equal((await send("finish")).ok, true);
    assert.ok(closeCount >= 1, "Finalization releases OPFS file lock");
    const decoded = Buffer.from(files.get(name).bytes).toString("utf8");
    assert.ok(decoded.startsWith(logLine));
    assert.equal((decoded.match(/EVENT/g) || []).length, 19);
    assert.equal((await send("append", {text: "late"})).ok, false,
      "Cannot write after finalization");
    assert.equal((await send("start", {name: "../danger"})).ok, false,
      "Private log names must be constrained");
    console.log("OPFS worker preserves every byte, flushes checkpoints and closes safely.");
  } catch (error) {
    console.error("OPFS automatic combat transcript worker regression failed", error);
    process.exitCode = 1;
  }
})();