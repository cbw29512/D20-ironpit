(() => {
  "use strict";
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  function apply(state, damageType, appliedAmount) {
    try {
      if (!(appliedAmount > 0)) return;
      for (const rule of (state.template.damage_taken_disadvantage_rules || [])) {
        if (rule.damageType !== damageType) continue;
        const expiry = (state.turn_serial || 0) + 1;
        const rows = [];
        if (rule.attackRollDisadvantage) rows.push([
          `${rule.id}:attack-roll-disadvantage`, "attack-roll-disadvantage",
        ]);
        if (rule.abilityCheckDisadvantage) rows.push([
          `${rule.id}:ability-check-disadvantage`, "ability-check-disadvantage",
        ]);
        for (const [id, kind] of rows) {
          state.active_modifiers = (state.active_modifiers || []).filter((item) => item.id !== id);
          M().add(state, {
            id,
            source_id: state.template.id,
            source_effect_id: rule.id,
            kind,
            flat_bonus: 0,
            dice_count: 0,
            dice_size: 0,
            damage_type: null,
            target_id: null,
            concentration_required: false,
            consume_on_attack_against: false,
            expires_at_start_of_source_turn: false,
            expires_at_end_of_target_turn: false,
            expires_target_turn_serial: expiry,
            expires_source_turn_end_round: null,
            expires_current_turn_end_owner_id: null,
            expires_current_turn_end_round: null,
          });
        }
      }
    } catch (error) {
      console.error("Browser damage-taken disadvantage failed.", {
        name: state?.template?.name, damageType, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_TAKEN_DISADVANTAGE = { apply };
})();
