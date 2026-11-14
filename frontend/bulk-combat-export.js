(() => {
  "use strict";
  // Export is explicitly user-triggered. The test itself never opens a picker.
  // OPFS -> user-selected file is a stream: no giant in-memory Blob.
  const $ = id => document.getElementById(id);
  let exporting = false;
  async function download() {
    const button = $("bulk-export");
    if (exporting || button?.disabled) return;
    let output = null;
    try {
      const name = window.IRON_PIT_BULK_COMBAT_FILE?.latestName();
      if (!name) throw new Error("No bulk test transcript has been recorded yet.");
      if (typeof window.showSaveFilePicker !== "function")
        throw new Error("Full-log export requires a current Chrome or Edge browser.");
      exporting = true;
      button.disabled = true;
      // This MUST be invoked directly from the click handler for user activation.
      const selected = window.showSaveFilePicker({
        suggestedName: name,
        types: [{description: "Complete combat transcript",
          accept: {"text/plain": [".txt"]}}],
      });
      $("bulk-status").textContent = "Preparing complete combat log download…";
      const destination = await selected;
      const root = await navigator.storage.getDirectory();
      const source = await root.getFileHandle(name);
      const file = await source.getFile();
      output = await destination.createWritable();
      $("bulk-status").textContent = "Exporting " + file.size.toLocaleString() +
        " bytes of complete combat logs…";
      await file.stream().pipeTo(output);
      output = null; // pipeTo closes the destination stream on success.
      $("bulk-status").textContent = "Full combat log saved: " + name;
    } catch (error) {
      if (output) {
        try { await output.abort(); }
        catch (abortError) { console.error("Could not abort failed log export", abortError); }
      }
      if (error?.name === "AbortError") {
        $("bulk-status").textContent = "Log download canceled; locally recorded results remain available.";
      } else {
        console.error("Full suite log export failed", error);
        $("bulk-status").textContent = "Log export failed: " + (error?.message || String(error));
      }
    } finally {
      exporting = false;
      if (button) button.disabled = $("bulk-stop")?.disabled === false ||
        !window.IRON_PIT_BULK_COMBAT_FILE?.latestName();
    }
  }
  window.IRON_PIT_BULK_COMBAT_EXPORT = {download};
})();