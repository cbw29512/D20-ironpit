(() => {
  "use strict";

  function matches(template, kind) {
    try {
      const expected = String(kind || "").trim().toLowerCase();
      if (!expected) return false;
      const raw = String(template?.creature_type || "");
      const base = raw.split(" (")[0].trim().toLowerCase();
      if (base === expected) return true;
      const open = raw.indexOf("("), close = raw.lastIndexOf(")");
      if (open < 0 || close <= open) return false;
      return raw.slice(open + 1, close).split(",")
        .some((part) => part.trim().toLowerCase() === expected);
    } catch (error) {
      console.error("Creature-kind matching failed", { kind, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_CREATURE_KIND = { matches };
})();
