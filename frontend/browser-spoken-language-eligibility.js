(() => {
  "use strict";
  // This is the browser peer of backend/app/combat/spoken_language_eligibility.py.
  // A missing languageProfile means unknown, not the Common language.
  const primordial = new Set(["primordial", "aquan", "auran", "ignan", "terran"]);

  function family(name) {
    if (typeof name !== "string" || !name.trim()) {
      throw new Error("Spoken-language evidence contains an invalid name.");
    }
    const normalized = name.trim().toLowerCase();
    return primordial.has(normalized) ? "primordial" : normalized;
  }

  function understood(speaker, listener) {
    try {
      // Require explicit immutable source profiles. Never infer a default.
      if (!speaker || !listener) return false;
      const spoken = speaker.spoken || [];
      const listens = listener.understood || [];
      if (!Array.isArray(spoken) || !Array.isArray(listens)) {
        throw new Error("Language evidence must contain spoken/understood arrays.");
      }
      if (speaker.speaksAll) return listener.understandsAll === true || listens.length > 0;
      if (listener.understandsAll) return spoken.length > 0;
      const known = new Set(spoken.map(family));
      return listens.some((name) => known.has(family(name)));
    } catch (error) {
      console.error("Spoken-language eligibility failed.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPOKEN_LANGUAGES = { understood };
})();
