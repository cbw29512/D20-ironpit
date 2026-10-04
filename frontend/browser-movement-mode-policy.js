(() => {
  "use strict";

  const MODE_FIELDS = { walk: "walk_ft", fly: "fly_ft", climb: "climb_ft", swim: "swim_ft", burrow: "burrow_ft" };
  const MODE_VERBS = { flies: "fly", swims: "swim", walks: "walk", climbs: "climb", burrows: "burrow" };
  const EXEMPTION_RE = /doesn['’]t provoke (?:an )?opportunity attacks? when it (flies|swims|walks|climbs|burrows) out of an enemy['’]?s reach/gi;

  function defaultHorizontalMovementMode(modes) {
    try {
      return (modes && Number(modes.fly_ft || 0) > 0) ? "fly" : "walk";
    } catch (error) {
      console.error("Failed to choose the default horizontal movement mode.", { error });
      throw error;
    }
  }

  function ensureActiveMovementMode(state) {
    try {
      if (!state.active_movement_mode) {
        state.active_movement_mode = defaultHorizontalMovementMode(state.template.movement_modes);
      }
      return state.active_movement_mode;
    } catch (error) {
      console.error("Failed to establish the active movement mode.", { error, combatant: state?.template?.name });
      throw error;
    }
  }

  function printedSpeedForState(state) {
    try {
      const mode = ensureActiveMovementMode(state);
      const field = MODE_FIELDS[mode];
      if (!field) throw new Error(`Unknown movement mode ${mode}.`);
      const speed = Number(state.template.movement_modes?.[field] || 0);
      return speed > 0 ? speed : Number(state.template.speed_ft || 0);
    } catch (error) {
      console.error("Failed to resolve printed movement-mode speed.", { error, combatant: state?.template?.name });
      throw error;
    }
  }

  function moverIsOpportunityAttackExempt(state) {
    try {
      const mode = ensureActiveMovementMode(state);
      return (state.template.opportunity_attack_exempt_movement_modes || []).includes(mode);
    } catch (error) {
      console.error("Failed to resolve movement-mode OA exemption.", { error, combatant: state?.template?.name });
      throw error;
    }
  }

  function exemptModesFromTraitText(sourceTraits) {
    try {
      const text = String(sourceTraits || "");
      if (!text.trim()) return [];
      const found = [];
      for (const match of text.matchAll(EXEMPTION_RE)) {
        const mode = MODE_VERBS[match[1].toLowerCase()];
        if (mode && !found.includes(mode)) found.push(mode);
      }
      return found;
    } catch (error) {
      console.error("Failed to parse movement-mode opportunity-attack exemptions.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MOVEMENT_MODE_POLICY = {
    defaultHorizontalMovementMode, ensureActiveMovementMode, exemptModesFromTraitText,
    moverIsOpportunityAttackExempt, printedSpeedForState,
  };
})();
