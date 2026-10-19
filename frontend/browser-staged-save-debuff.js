(() => {
  "use strict";
  function resolve({ saveTotal, dc, initialEffect, terminalEffect, previousEffect = null,
                     immediateFailureMargin = null }) {
    if (!Number.isInteger(saveTotal) || !Number.isInteger(dc) || dc < 1 ||
        typeof initialEffect !== "string" || !initialEffect.trim() ||
        typeof terminalEffect !== "string" || !terminalEffect.trim() ||
        initialEffect === terminalEffect ||
        (previousEffect !== null && previousEffect !== initialEffect) ||
        (immediateFailureMargin !== null &&
         (!Number.isInteger(immediateFailureMargin) || immediateFailureMargin < 1))) {
      throw new Error("Invalid staged saving throw configuration.");
    }
    if (saveTotal >= dc) return null;
    if (previousEffect === initialEffect ||
        (immediateFailureMargin !== null && dc - saveTotal >= immediateFailureMargin)) return terminalEffect;
    return initialEffect;
  }
  window.IRON_PIT_BROWSER_STAGED_SAVE_DEBUFF = { resolve };
})();
