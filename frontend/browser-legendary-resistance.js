(() => {
  "use strict";
  const RESOURCE_ID = "legendary-resistance";
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;

  function use(state) {
    const defined = Object.prototype.hasOwnProperty.call(state.template.resources || {}, RESOURCE_ID);
    if (!defined) return false;
    const resources = RES();
    if (!resources) throw new Error("Browser resource API is not loaded.");
    if (!resources.available(state, RESOURCE_ID)) return false;
    resources.spend(state, RESOURCE_ID);
    return true;
  }

  window.IRON_PIT_BROWSER_LEGENDARY_RESISTANCE = { use };
})();
