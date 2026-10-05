(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  let lastBattle = null;

  function remember(battle) {
    try {
      lastBattle = battle && Array.isArray(battle.events) && battle.events.length ? battle : null;
      const button = el("download-log-button");
      if (button) button.disabled = !lastBattle;
    } catch (error) {
      console.error("Fight log export state could not be updated", error);
      throw error;
    }
  }

  function textFromBattle(battle) {
    const formatter = window.IRON_PIT_BATTLE_LOG;
    if (!formatter?.format) throw new Error("Battle log formatter is missing.");
    const events = battle?.events;
    if (!Array.isArray(events) || !events.length) throw new Error("No fight log is available to download.");
    const lines = [];
    for (const event of events) {
      lines.push(`Round ${event.round_number} · ${event.event_type || "Combat event"}`);
      lines.push(formatter.format(event));
      for (const step of event.audit?.steps || []) {
        const label = step.rule || step.step || "Resolution";
        const detail = step.detail || step.outcome || "Applied.";
        lines.push(`  - ${label}: ${detail}`);
      }
      lines.push("");
    }
    return lines.join("\n").trim();
  }

  function download() {
    try {
      const text = `${textFromBattle(lastBattle)}\n`;
      const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `iron-pit-fight-log-${new Date().toISOString().replace(/[:.]/g, "-")}.txt`;
      document.body.append(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Fight log download failed", error);
      const status = el("status");
      if (status) status.textContent = "Could not download the fight log.";
    }
  }

  function install() {
    const button = el("download-log-button");
    if (!button) throw new Error("Download log control is missing.");
    button.disabled = true;
    button.addEventListener("click", download);
  }

  window.IRON_PIT_BATTLE_LOG_EXPORT = { download, install, remember, textFromBattle };
})();
