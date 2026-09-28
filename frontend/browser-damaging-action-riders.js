(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;

  function actionDealtDamage(events) {
    try {
      return (events || []).some((event) =>
        (event.damage_components || []).some((component) => (component.applied_total || 0) > 0)
      );
    } catch (error) {
      console.error("Browser damaging-action rider could not inspect damage", { error });
      throw error;
    }
  }

  function effectiveMaxHp(state) {
    return Math.max(1, (state.template.max_hp || 0) + (state.max_hp_bonus || 0));
  }

  function chooseTarget(actor, setup, amount, rule) {
    try {
      const allies = actor.side === "heroes" ? setup.heroes : setup.monsters;
      const legal = allies.filter((target) => {
        if (target.state.is_dead) return false;
        if (rule.target_mode === "self" && target.combatant_id !== actor.combatant_id) return false;
        if (rule.target_mode === "self_or_ally"
            && Math.abs(target.position_ft - actor.position_ft) > (rule.range_ft || 0)) return false;
        return (target.state.temporary_hp || 0) < amount;
      });
      if (!legal.length) return null;
      legal.sort((left, right) => {
        const leftRatio = left.state.current_hp / effectiveMaxHp(left.state);
        const rightRatio = right.state.current_hp / effectiveMaxHp(right.state);
        if (leftRatio !== rightRatio) return leftRatio - rightRatio;
        const leftTemp = left.state.temporary_hp || 0;
        const rightTemp = right.state.temporary_hp || 0;
        if (leftTemp !== rightTemp) return leftTemp - rightTemp;
        return left.combatant_id.localeCompare(right.combatant_id);
      });
      return legal[0];
    } catch (error) {
      console.error("Browser damaging-action rider target selection failed", { error });
      throw error;
    }
  }

  function resolve(sequence, round, actor, setup, actionId, events) {
    try {
      const rule = actor.state.template.damaging_action_temporary_hp_rider;
      if (!rule || !(rule.action_ids || []).includes(actionId) || !actionDealtDamage(events)) return null;
      const score = actor.state.template.ability_scores?.[rule.ability];
      if (!Number.isInteger(score)) {
        throw new Error("Ability-scaled Temporary HP requires a certified ability score.");
      }
      const amount = Math.max(0, Math.floor((score - 10) / 2) * (rule.multiplier || 1));
      const target = chooseTarget(actor, setup, amount, rule);
      if (!target) return null;
      const before = target.state.temporary_hp || 0;
      if (!S()?.grantTemporaryHp) throw new Error("Browser Temporary HP runtime is not loaded.");
      const after = S().grantTemporaryHp(target.state, amount);
      if (after <= before) return null;
      return {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: actor.combatant_id,
        actor_name: actor.state.template.name,
        target_id: target.combatant_id,
        target_name: target.state.template.name,
        temporary_hp_before: before,
        temporary_hp_after: after,
        feature_id: rule.source_id,
        animation: "temporary-hp",
        description: `${actor.state.template.name} grants ${target.state.template.name} ${after - before} Temporary HP with ${rule.source_name}.`,
      };
    } catch (error) {
      console.error("Browser damaging-action Temporary HP resolution failed", {
        actor: actor?.combatant_id, actionId, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGING_ACTION_RIDERS = { actionDealtDamage, chooseTarget, resolve };
})();
