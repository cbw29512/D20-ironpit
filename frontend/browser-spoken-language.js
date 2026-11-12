(() => {
  "use strict";

  // Same semantic contract as Python: unknown language matches fail closed.
  function understands(casterTemplate, targetTemplate) {
    try {
      const spoken = new Set((casterTemplate.spoken_languages || [])
        .map((item) => String(item).toLowerCase()));
      const understood = new Set((targetTemplate.understood_languages || [])
        .map((item) => String(item).toLowerCase()));
      if (!spoken.size || !understood.size) return false;
      return spoken.has("all") || understood.has("all")
        || [...spoken].some((item) => understood.has(item));
    } catch (error) {
      console.error("Shared spoken-language compatibility failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPOKEN_LANGUAGE = { understands };
})();
