"use strict";
const assert = require("node:assert/strict");
// Small browser fixture: a private local transcript store and user-initiated export.
function makeContext(controls) {
  const files = [], downloads = [], messages = [];
  const byName = new Map(), pointer = new Map();
  const picks = {count: 0};
  class Worker {
    constructor(source) {
      assert.equal(source, "bulk-combat-log-worker.js");
      this.active = null;
    }
    postMessage(request) {
      queueMicrotask(() => {
        try {
          const {action, name, text, id} = request;
          if (action === "start") {
            this.active = {name, parts: [], closed: false};
            files.push(this.active); byName.set(name, this.active);
          } else if (action === "append") {
            if (!this.active || this.active.closed) throw new Error("Log is closed.");
            this.active.parts.push(text);
          } else if (action === "finish") {
            if (!this.active) throw new Error("No log is active.");
            this.active.closed = true;
          } else throw new Error("Invalid worker action.");
          this.onmessage({data: {id, ok: true}});
        } catch (error) {
          this.onmessage({data: {id: request.id, ok: false, error: error.message}});
        }
      });
    }
    terminate() {}
  }
  const context = {console, setTimeout, clearTimeout, Blob, URL, Date, Worker,
    localStorage: {
      setItem: (key, value) => pointer.set(key, value),
      getItem: key => pointer.get(key) || null,
    },
    document: {getElementById: id => controls[id] || null},
    navigator: {
      clipboard: {async writeText(value) { messages.push(value); }},
      storage: {async getDirectory() { return {
        async getFileHandle(name) { return {
          async getFile() {
            const record = byName.get(name);
            if (!record) throw new Error("Transcript missing from OPFS.");
            return {
              size: Buffer.byteLength(record.parts.join("")),
              stream: () => ({async pipeTo(destination) {
                for (const part of record.parts) await destination.write(part);
                await destination.close();
              }}),
            };
          },
        }; },
      }; }},
    },
  };
  context.window = context;
  context.showSaveFilePicker = () => {
    picks.count++;
    const saved = {parts: [], closed: false};
    downloads.push(saved);
    return Promise.resolve({async createWritable() { return {
      async write(part) { saved.parts.push(part); },
      async close() { saved.closed = true; },
      async abort() { saved.closed = true; },
    }; }});
  };
  return {context, files, picks, downloads, messages};
}
module.exports = {makeContext};