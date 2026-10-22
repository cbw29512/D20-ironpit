(() => {
  "use strict";
  const KEY = "iron-pit-custom-combatants-v1";
  function load() {
    try {
      const data = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(data) ? data.filter(item => item && (item.kind === "monster" || item.kind === "character") && typeof item.id === "string") : [];
    } catch { return []; }
  }
  function save(draft) {
    if (!draft || !["monster", "character"].includes(draft.kind) || !/^[a-z0-9][a-z0-9-]*$/.test(draft.id))
      throw new Error("Invalid custom combatant.");
    const all = load();
    const scopedId = draft.ruleset + ":" + draft.kind + ":" + draft.id;
    const copy = JSON.parse(JSON.stringify(draft));
    copy.custom = true;
    copy.coverage_status = "custom_draft";
    copy.runnable_template_id = null;
    const index = all.findIndex(item => item.ruleset + ":" + item.kind + ":" + item.id === scopedId);
    if (index < 0) all.push(copy); else all[index] = copy;
    try { localStorage.setItem(KEY, JSON.stringify(all)); }
    catch { throw new Error("Couldn't save custom card in this browser. Check available storage."); }
    return copy;
  }
  const api = {load, save, list: (kind, ruleset) => load().filter(row => row.kind === kind && row.ruleset === ruleset)};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.IRON_PIT_CUSTOM_LIBRARY = api;
})();
