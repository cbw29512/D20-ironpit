(() => {
  "use strict";

  function roster(setup, side) {
    return side === "heroes" ? setup.heroes : setup.monsters;
  }

  function memberAt(setup, side, rosterIndex) {
    const rows = roster(setup, side);
    if (rosterIndex < 1 || rosterIndex > rows.length) {
      throw new Error(`Opening condition roster index ${rosterIndex} is outside ${side}.`);
    }
    return rows[rosterIndex - 1];
  }

  function apply(setup, selection) {
    try {
      const bindings = selection.opening_conditions || [];
      if (!bindings.length) return;
      const T = window.IRON_PIT_BROWSER_TIMED;
      if (!T?.apply) throw new Error("Opening conditions require browser-timed-conditions.js.");
      for (const binding of bindings) {
        const target = memberAt(setup, binding.side, binding.roster_index);
        const source = memberAt(setup, binding.source_side, binding.source_roster_index);
        T.apply(target.state, binding.condition_id, source.combatant_id, {
          sourceTemplate: source.state.template,
          sourceIsMagical: true,
          appliedRound: 0,
        });
      }
    } catch (error) {
      console.error("Failed to apply browser opening conditions", { error });
      throw error;
    }
  }

  function events(sequence, setup, selection) {
    try {
      const rows = [];
      for (const binding of selection.opening_conditions || []) {
        const target = memberAt(setup, binding.side, binding.roster_index);
        const source = memberAt(setup, binding.source_side, binding.source_roster_index);
        if (!(target.state.active_effect_ids || []).includes(binding.condition_id)) continue;
        rows.push({
          sequence: sequence++,
          round_number: 0,
          event_type: "feature",
          actor_id: source.combatant_id,
          actor_name: source.state.template.name,
          target_id: target.combatant_id,
          target_name: target.state.template.name,
          applied_condition_ids: [binding.condition_id],
          feature_id: "opening-condition",
          animation: "condition",
          description: `${target.state.template.name} begins the fight ${binding.condition_id} because of ${source.state.template.name}.`,
        });
      }
      return { events: rows, sequence };
    } catch (error) {
      console.error("Failed to audit browser opening conditions", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_OPENING_CONDITIONS = { apply, events, memberAt };
})();
