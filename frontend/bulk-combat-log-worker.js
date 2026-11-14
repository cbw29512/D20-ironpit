(() => {
  "use strict";
  // Dedicated worker: writes the full transcript to OPFS without blocking UI.
  // State is one locked file, byte offset, and flush checkpoint counter.
  let handle = null, offset = 0, writes = 0;
  const encoder = new TextEncoder();
  self.onmessage = async ({data}) => {
    const {id, action} = data || {};
    try {
      if (action === "start") {
        if (handle) throw new Error("Another bulk transcript is already active.");
        const name = String(data.name || "");
        if (!/^iron-pit-(bag|pairs)-complete-\d+-\d+\.txt$/.test(name))
          throw new Error("Invalid private combat transcript filename.");
        const root = await navigator.storage.getDirectory();
        const file = await root.getFileHandle(name, {create: true});
        handle = await file.createSyncAccessHandle();
        handle.truncate(0);
        offset = 0;
        writes = 0;
      } else if (action === "append") {
        if (!handle) throw new Error("No active bulk transcript.");
        const bytes = encoder.encode(String(data.text ?? ""));
        let done = 0;
        while (done < bytes.length) {
          const amount = handle.write(bytes.subarray(done), {at: offset});
          if (!Number.isInteger(amount) || amount < 1)
            throw new Error("Partial or zero-byte combat log write.");
          done += amount;
          offset += amount;
        }
        // Commit a checkpoint at most every 20 fight writes.
        if (++writes % 20 === 0) handle.flush();
      } else if (action === "finish") {
        if (!handle) throw new Error("No active transcript to finalize.");
        handle.flush();
        handle.close();
        handle = null;
      } else {
        throw new Error("Unknown combat log action: " + action);
      }
      self.postMessage({id, ok: true, bytes: offset});
    } catch (error) {
      console.error("Private combat log operation failed", {action, error});
      try { handle?.flush(); handle?.close(); }
      catch (closeError) { console.error("Failed to release private combat log", closeError); }
      handle = null;
      self.postMessage({id, ok: false, error: error?.message || String(error)});
    }
  };
})();