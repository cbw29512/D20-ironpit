(() => {
  "use strict";
  // The single-fight page keeps only the selected combat transcript; bulk
  // results never share memory or export paths with individual tests.
  const $ = id => document.getElementById(id);
  function transcript() {
    try {
      const content = $("events")?.textContent || "";
      if (!content.startsWith("IRON PIT — COMPLETE PREGEN FIGHT"))
        throw new Error("Run a prepared pregen fight first.");
      return content;
    } catch (error) {
      console.error("Selected pregen transcript is unavailable", error);
      throw error;
    }
  }
  async function copy() {
    try {
      await navigator.clipboard.writeText(transcript());
      $("summary").textContent = "Complete combat transcript copied.";
    } catch (error) {
      console.error("Could not copy pregen transcript", error);
      $("summary").textContent = "Copy failed: " + error.message;
    }
  }
  function download() {
    try {
      const blob = new Blob([transcript()], {type: "text/plain;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "iron-pit-pregen-fight-" + Date.now() + ".txt";
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
    } catch (error) {
      console.error("Could not download pregen transcript", error);
      $("summary").textContent = "Download failed: " + error.message;
    }
  }
  try {
    $("pregen-copy").addEventListener("click", () => { void copy(); });
    $("pregen-save").addEventListener("click", download);
  } catch (error) {
    console.error("Could not install pregen transcript controls", error);
    throw error;
  }
})();