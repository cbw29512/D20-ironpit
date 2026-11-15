(() => {
  "use strict";

  // The shared effect-removal resolver spends the Action and spell resource.
  // This module resolves all independent spell effects on ONE chosen creature.
  function preflight(remover, setup, action, target, effects) {
    try {
      const candidates = effects.filter((item) => !item.grant
        && item.target.combatant_id === target.combatant_id);
      if (!candidates.length) throw new Error("No tracked spell effects remain.");
      if (candidates.some((item) => item.spellLevel > (action.autoRemoveMaxLevel ?? 3))) {
        if (!Number.isInteger(remover.state.template.ability_scores?.[action.castingAbility])
          || typeof window.IRON_PIT_BROWSER_ROLLS?.d20 !== "function") {
          throw new Error("Higher-level Dispel Magic requires a casting score and dice.");
        }
      }
      return candidates;
    } catch (error) {
      console.error("Multi-effect Dispel Magic preflight failed", error);
      throw error;
    }
  }

  function apply(sequence, round, remover, setup, action, target, candidates, remaining) {
    try {
      const A = window.IRON_PIT_BROWSER_ABILITY_CHECKS;
      const R = window.IRON_PIT_BROWSER_ROLLS;
      const M = window.IRON_PIT_BROWSER_MODIFIERS;
      const removed = [], steps = [], summary = [];
      let firstCheck = null, firstDc = null;
      for (const item of candidates) {
        let check = null, dc = null, succeeded = true;
        if (item.spellLevel > (action.autoRemoveMaxLevel ?? 3)) {
          dc = 10 + item.spellLevel;
          const score = remover.state.template.ability_scores[action.castingAbility];
          check = R.d20(Math.floor((score - 10) / 2),
            A?.mode?.(remover.state, 0, 0, {ability: action.castingAbility}) || "normal");
          const result = A?.resolve
            ? A.resolve(remover.state, action.castingAbility, check, dc, {roller: remover, setup})
            : {roll: check, succeeded: check.total >= dc};
          check = result.roll;
          succeeded = result.succeeded;
          if (!firstCheck) {firstCheck = check; firstDc = dc;}
          steps.push({phase: "hit_or_save_check", kind: "check",
            label: `${item.effectId} level ${item.spellLevel}: Dispel Magic check ${check.total} vs DC ${dc}; ${succeeded ? "success" : "failure"}`});
        } else {
          steps.push({phase: "hit_or_save_check", kind: "rule",
            label: `${item.effectId} level ${item.spellLevel}: automatic dispel`});
        }
        if (succeeded) {
          M.removeSource([target.state], item.source.combatant_id, item.effectId);
          target.state.active_buff_effect_ids = (target.state.active_buff_effect_ids || [])
            .filter((id) => id !== item.effectId);
          removed.push(item.effectId);
        }
        summary.push(`${item.effectId}: ${succeeded ? "ended" : "resisted"}`);
      }
      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: remover.combatant_id, actor_name: remover.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        ability_check_roll: firstCheck, check_ability: firstCheck ? action.castingAbility : null,
        check_dc: firstDc, feature_id: action.id, resource_remaining: remaining,
        removed_condition_ids: removed, animation: action.animation || "effect-removal",
        audit: {steps},
        description: `${remover.state.template.name} uses ${action.name} on ${target.state.template.name}: ${summary.join("; ")}.`,
      };
    } catch (error) {
      console.error("Multi-effect Dispel Magic resolution failed", error);
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_EFFECT_REMOVAL_MULTI = {preflight, apply};
})();
