(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  let bundlePromise = null;

  function ensureBundle(ruleset) {
    if (ruleset !== "2014") return Promise.resolve();
    if (window.IRON_PIT_2014_MVP_READY === true && window.IRON_PIT_BROWSER_MONSTERS_2014) return Promise.resolve();
    if (bundlePromise) return bundlePromise;
    bundlePromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "browser-monsters-2014.js";
      script.async = true;
      script.dataset.ironPitRuleset = "2014";
      script.onload = () => window.IRON_PIT_2014_MVP_READY === true
        ? resolve()
        : reject(new Error("2014 browser bundle loaded without its readiness marker."));
      script.onerror = () => reject(new Error("2014 browser bundle could not be loaded."));
      document.head.append(script);
    });
    return bundlePromise;
  }

  function summary(state) {
    if (!state.catalog) return "";
    if (state.ruleset === "2014") {
      return `${state.catalog.hero_ready_count} heroes · ${state.catalog.monster_ready_count} monsters ready for 2014 fights.`;
    }
    return `${state.catalog.hero_ready_count} heroes · ${state.catalog.monster_ready_count} monsters ready for 2024 fights.`;
  }

  function update(state) {
    try {
      const is2014 = state.ruleset === "2014";
      const eyebrow = el("ruleset-eyebrow") || document.querySelector("header.pit-chrome p.eyebrow, header.hero p.eyebrow");
      const editionNote = el("ruleset-edition-note");
      if (eyebrow) eyebrow.textContent = is2014 ? "D&D 5e 2014" : "D&D 5e 2024";
      if (editionNote) editionNote.textContent = is2014
        ? "2014 is selected. Switch to 2024 to use that edition's heroes and monsters."
        : "2024 is selected. Switch to 2014 to use that edition's heroes and monsters.";
      const auditNote = document.querySelector(".log-panel .rules-note");
      if (auditNote) auditNote.textContent = is2014 ? "2014 rules" : "2024 rules";
      const left = document.querySelector(".hero-field .field-heading span"), right = document.querySelector(".monster-field .field-heading span");
      if (left) left.textContent = "Heroes";
      if (right) right.textContent = "Monsters";
      el("ruleset-summary").textContent = summary(state);
      el("ruleset-control").dataset.ruleset = state.ruleset;
      el("ruleset-select").value = state.ruleset;
    } catch (error) {
      console.error("Ruleset presentation update failed", { ruleset: state?.ruleset, error });
    }
  }

  function syncDisabled(state) {
    const active = Boolean(state.session && !state.session.complete);
    el("ruleset-select").disabled = state.fighting || active;
  }

  function install(state, onChange) {
    const control = el("ruleset-control"), select = el("ruleset-select"), note = el("ruleset-summary");
    if (!control || !select || !note) throw new Error("Static ruleset control is missing from the Iron Pit page.");
    control.dataset.ruleset = state.ruleset;
    select.value = state.ruleset;
    select.addEventListener("change", () => onChange(select.value));
  }

  window.IRON_PIT_RULESET_UI = { ensureBundle, install, syncDisabled, update };
})();
