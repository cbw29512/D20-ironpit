(() => {
  "use strict";

  const sourceLabel = (id) => String(id || "bonus").split("-").map((part) => part ? part[0].toUpperCase() + part.slice(1) : "").join(" ");
  const conditionLabel = (id) => sourceLabel(String(id || "condition").replaceAll("_", "-"));

  function rollLabel(roll) {
    if (!roll) return "AUTO FAIL";
    const natural = roll.selected_roll;
    const mode = roll.mode === "advantage" ? "ADV" : roll.mode === "disadvantage" ? "DIS" : "d20";
    const d20Count = roll.mode === "normal" || !roll.mode ? 1 : 2;
    const d20Rolls = (roll.rolls || []).slice(0, d20Count);
    const pool = d20Rolls.length > 1 ? ` [${d20Rolls.join(", ")}]` : "";
    const modifier = Number(roll.modifier || 0), signed = modifier >= 0 ? `+ ${modifier}` : `- ${Math.abs(modifier)}`;
    const bonuses = (roll.bonus_dice || []).map((bonus) =>
      ` + ${sourceLabel(bonus.source_effect_id)} ${bonus.notation} [${bonus.rolls.join(", ")}]`).join("");
    return `${mode}${pool} ${natural} ${signed}${bonuses} = ${roll.total}`;
  }

  function damageLabel(event) {
    if (!event.damage_roll) return "";
    const parts = (event.damage_components || []).map((part) => {
      const applied = part.applied_total ?? part.total, type = part.damage_type || "damage";
      return applied === part.total ? `${applied} ${type}` : `${applied} ${type} (${part.total} before defenses → ${applied} after defenses)`;
    });
    return parts.length ? parts.join(" + ") : `${event.damage_roll.total} damage`;
  }

  function stateLines(event, { includeConditions = true, damaged = true } = {}) {
    const lines = [];
    if (event.temporary_hp_before != null && event.temporary_hp_after != null && event.temporary_hp_before !== event.temporary_hp_after) lines.push(`Temp HP: ${event.temporary_hp_before} → ${event.temporary_hp_after}.`);
    if (damaged && event.hp_before != null && event.hp_after != null && event.hp_before !== event.hp_after) lines.push(`HP: ${event.target_name || "Target"} ${event.hp_before} → ${event.hp_after}.`);
    if (includeConditions && event.applied_condition_ids?.length) lines.push(`Condition: ${event.target_name || "Target"} gains ${event.applied_condition_ids.map(conditionLabel).join(", ")}.`);
    if (event.removed_condition_ids?.length) lines.push(`Condition ended: ${event.removed_condition_ids.map(conditionLabel).join(", ")}.`);
    if (event.concentration_ended_effect_id) lines.push(`Concentration ended: ${sourceLabel(event.concentration_ended_effect_id)}.`);
    if (event.is_dead) lines.push(`${event.target_name || "Target"} is DEAD.`);
    return lines;
  }

  function attackDeathLine(event) {
    if (!event.hit || event.hp_before !== 0 || event.death_save_failures == null) return "";
    const added = event.critical ? 2 : 1;
    return `Damage at 0 HP: +${added} death failure${added === 1 ? "" : "s"} (now ${event.death_save_failures}).`;
  }

  function attemptedConditions(event, context) {
    const explicit = context?.attemptedConditionIds || [];
    if (explicit.length) return [...new Set(explicit)];
    return event.save_succeeded === false ? [...new Set(event.applied_condition_ids || [])] : [];
  }

  function formatInitiativeLines(event) {
    const description = event.description || `${event.actor_name || "Combatant"} rolls initiative.`;
    return event.attack_roll ? [description, `Initiative roll: ${rollLabel(event.attack_roll)}.`] : [description];
  }

  function formatAttackLines(event, context = {}) {
    const natural = event.attack_roll?.selected_roll;
    const result = natural === 1 ? "NAT 1 · MISS" : event.critical ? "CRITICAL HIT" : event.hit ? "HIT" : "MISS";
    const attackName = event.attack_name || event.weapon_name || event.weapon_id || event.feature_id || "attack";
    const mastery = event.feature_id === "weapon-mastery-cleave" ? " [CLEAVE]" : "";
    const lines = [`${event.actor_name} uses ${attackName}${mastery} on ${event.target_name}.`];
    if (event.attack_roll) lines.push(`Attack: ${rollLabel(event.attack_roll)}${event.target_ac == null ? "" : ` vs AC ${event.target_ac}`} — ${result}.`);
    const damage = damageLabel(event);
    if (damage) lines.push(`Damage: ${damage}.`);
    lines.push(...stateLines(event, { includeConditions: false, damaged: Boolean(event.hit) }));

    if (event.save_dc != null) {
      const conditions = attemptedConditions(event, context);
      const effect = conditions.length ? conditions.map(conditionLabel).join(", ") : "secondary effect";
      lines.push(`${attackName} triggers ${effect} · ${String(event.save_ability || "save").toUpperCase()} DC ${event.save_dc}.`);
      lines.push(`Save: ${event.target_name} rolls ${rollLabel(event.saving_throw_roll)} — ${event.save_succeeded ? "SUCCESS" : "FAILURE"}.`);
      if (conditions.length) {
        const applied = new Set(event.applied_condition_ids || []);
        const appliedLabels = conditions.filter((id) => applied.has(id)).map(conditionLabel);
        const resistedLabels = conditions.filter((id) => !applied.has(id)).map(conditionLabel);
        if (appliedLabels.length) lines.push(`Condition: ${event.target_name} gains ${appliedLabels.join(", ")}.`);
        if (resistedLabels.length) lines.push(`Condition: ${event.target_name} resists ${resistedLabels.join(", ")}.`);
      } else if (event.applied_condition_ids?.length) {
        lines.push(`Condition: ${event.target_name} gains ${event.applied_condition_ids.map(conditionLabel).join(", ")}.`);
      }
    } else if (event.applied_condition_ids?.length) {
      lines.push(`Condition: ${event.target_name} gains ${event.applied_condition_ids.map(conditionLabel).join(", ")}.`);
    }

    const death = attackDeathLine(event); if (death) lines.push(death);
    return lines;
  }

  function formatSaveLines(event, context = {}) {
    const result = event.save_succeeded ? "SUCCESS" : "FAILURE";
    const source = event.feature_id ? sourceLabel(event.feature_id) : "effect";
    const lines = [`${event.actor_name} uses ${source} on ${event.target_name}.`, `Save: ${event.target_name} rolls ${rollLabel(event.saving_throw_roll)} vs DC ${event.save_dc} — ${result}.`];
    const damage = damageLabel(event); if (damage) lines.push(`Damage: ${damage}.`);
    const conditions = attemptedConditions(event, context);
    if (conditions.length) {
      const applied = new Set(event.applied_condition_ids || []);
      const appliedLabels = conditions.filter((id) => applied.has(id)).map(conditionLabel);
      const resistedLabels = conditions.filter((id) => !applied.has(id)).map(conditionLabel);
      if (appliedLabels.length) lines.push(`Condition: ${event.target_name} gains ${appliedLabels.join(", ")}.`);
      if (resistedLabels.length) lines.push(`Condition: ${event.target_name} resists ${resistedLabels.join(", ")}.`);
    }
    lines.push(...stateLines(event, { includeConditions: !conditions.length, damaged: Boolean(event.damage_roll) }));
    return lines;
  }

  function counterLabel(name, before, after) {
    if (after == null) return "";
    return before == null ? `${name} ${after}` : `${name} ${before}→${after}`;
  }

  function formatDeathSaveLines(event) {
    const natural = event.death_save_roll?.selected_roll;
    const tag = natural === 1 ? "NAT 1" : natural === 20 ? "NAT 20" : `d20 ${natural}`;
    const lines = [`${event.actor_name}: Death Save ${tag}.`];
    const counters = [counterLabel("successes", event.death_save_successes_before, event.death_save_successes), counterLabel("failures", event.death_save_failures_before, event.death_save_failures)].filter(Boolean);
    if (counters.length) lines.push(`Death saves: ${counters.join(" · ")}.`);
    if (natural === 1) lines.push("Natural 1 = two failures.");
    if (natural === 20) lines.push("Natural 20 = regains 1 HP.");
    if (event.is_stable) lines.push("STABLE."); if (event.is_dead) lines.push("DEAD.");
    return lines;
  }

  function compactEvents(events = []) {
    const compacted = [];
    for (const event of events) {
      const previous = compacted[compacted.length - 1];
      const mergeMovement = event.event_type === "movement" && previous?.event_type === "movement"
        && previous.actor_id === event.actor_id && previous.round_number === event.round_number;
      if (!mergeMovement) {
        compacted.push({ ...event });
        continue;
      }
      const movement = Number(previous.movement_ft || 0) + Number(event.movement_ft || 0);
      const cost = Number(previous.movement_cost_ft || 0) + Number(event.movement_cost_ft || 0);
      const merged = { ...previous, ...event, movement_ft: movement };
      if (previous.movement_cost_ft != null || event.movement_cost_ft != null) merged.movement_cost_ft = cost;
      if (previous.grid_path || event.grid_path) merged.grid_path = [...(previous.grid_path || []), ...(event.grid_path || [])];
      merged.description = `${event.actor_name || previous.actor_name || "Combatant"} moves ${movement} feet.`;
      compacted[compacted.length - 1] = merged;
    }
    return compacted;
  }

  function formatLines(event, context = {}) {
    if (event.event_type === "initiative") return formatInitiativeLines(event);
    if (event.event_type === "attack") return formatAttackLines(event, context);
    if (event.event_type === "saving_throw") return formatSaveLines(event, context);
    if (event.event_type === "death_save") return formatDeathSaveLines(event);
    if (event.event_type === "healing" && event.target_name && event.hp_before != null && event.hp_after != null) return [event.description || `${event.actor_name} heals ${event.target_name}.`, `HP: ${event.target_name} ${event.hp_before} → ${event.hp_after}.`];
    return [event.description || `${event.actor_name || "Arena"}: ${event.event_type}`];
  }

  function format(event, context = {}) { return formatLines(event, context).join(" · "); }

  window.IRON_PIT_BATTLE_LOG = {
    compactEvents, format, formatLines,
    formatAttack: (event, context = {}) => formatAttackLines(event, context).join(" · "),
    formatDeathSave: (event) => formatDeathSaveLines(event).join(" · "),
    formatInitiative: (event) => formatInitiativeLines(event).join(" · "),
    formatSave: (event, context = {}) => formatSaveLines(event, context).join(" · "),
    rollLabel,
  };
})();