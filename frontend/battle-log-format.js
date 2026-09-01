(() => {
  "use strict";

  const sourceLabel = (id) => String(id || "bonus").split("-").map((part) => part ? part[0].toUpperCase() + part.slice(1) : "").join(" ");

  function rollLabel(roll) {
    if (!roll) return "AUTO FAIL";
    const natural = roll.selected_roll;
    const mode = roll.mode === "advantage" ? "ADV" : roll.mode === "disadvantage" ? "DIS" : "d20";
    const d20Count = roll.mode === "normal" || !roll.mode ? 1 : 2;
    const d20Rolls = (roll.rolls || []).slice(0, d20Count);
    const pool = d20Rolls.length > 1 ? ` [${d20Rolls.join(", ")}]` : "";
    const modifier = Number(roll.modifier || 0), signed = modifier >= 0 ? `+${modifier}` : String(modifier);
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

  function concentrationLabel(event) {
    return event.concentration_ended_effect_id ? `Concentration ended: ${sourceLabel(event.concentration_ended_effect_id)}` : "";
  }

  function attackDeathLabel(event) {
    if (!event.hit || event.hp_before !== 0 || event.death_save_failures == null) return "";
    const added = event.critical ? 2 : 1;
    return `damage at 0 HP: +${added} Death failure${added === 1 ? "" : "s"} (now ${event.death_save_failures})`;
  }

  function appendState(pieces, event, damaged = true) {
    if (event.temporary_hp_before != null && event.temporary_hp_after != null && event.temporary_hp_before !== event.temporary_hp_after) pieces.push(`Temp HP ${event.temporary_hp_before}→${event.temporary_hp_after}`);
    if (damaged && event.hp_before != null && event.hp_after != null) pieces.push(`HP ${event.hp_before}→${event.hp_after}`);
    if (event.applied_condition_ids?.length) pieces.push(event.applied_condition_ids.map((id) => id.toUpperCase()).join(", "));
    if (event.removed_condition_ids?.length) pieces.push(`ended ${event.removed_condition_ids.map(sourceLabel).join(", ")}`);
    const concentration = concentrationLabel(event); if (concentration) pieces.push(concentration);
    if (event.is_dead) pieces.push("DEAD");
  }

  function formatAttack(event) {
    const natural = event.attack_roll?.selected_roll;
    const result = natural === 1 ? "NAT 1 · MISS" : event.critical ? "CRITICAL HIT" : event.hit ? "HIT" : "MISS";
    const attackName = event.attack_name || event.weapon_name || event.weapon_id || event.feature_id || "attack";
    const pieces = [`${event.actor_name} → ${event.target_name}: ${result} with ${attackName}`];
    if (event.attack_roll) pieces.push(`${rollLabel(event.attack_roll)}${event.target_ac == null ? "" : ` vs AC ${event.target_ac}`}`);
    const damage = damageLabel(event); if (damage) pieces.push(damage);
    appendState(pieces, event, Boolean(event.hit));
    const death = attackDeathLabel(event); if (death) pieces.push(death);
    return pieces.join(" · ");
  }

  function formatSave(event) {
    const result = event.save_succeeded ? "SUCCEEDS" : "FAILS";
    const ability = String(event.save_ability || "save").toUpperCase();
    const source = event.feature_id ? sourceLabel(event.feature_id) : "effect";
    const pieces = [`${event.target_name} ${result} ${ability} save vs ${event.actor_name}'s ${source}`];
    pieces.push(`${rollLabel(event.saving_throw_roll)} vs DC ${event.save_dc}`);
    const damage = damageLabel(event); if (damage) pieces.push(damage);
    appendState(pieces, event, Boolean(event.damage_roll));
    return pieces.join(" · ");
  }

  function counterLabel(name, before, after) {
    if (after == null) return "";
    return before == null ? `${name} ${after}` : `${name} ${before}→${after}`;
  }

  function formatDeathSave(event) {
    const natural = event.death_save_roll?.selected_roll;
    const tag = natural === 1 ? "NAT 1" : natural === 20 ? "NAT 20" : `d20 ${natural}`;
    const pieces = [`${event.actor_name}: Death Save ${tag}`,
      counterLabel("successes", event.death_save_successes_before, event.death_save_successes),
      counterLabel("failures", event.death_save_failures_before, event.death_save_failures)].filter(Boolean);
    if (natural === 1) pieces.push("natural 1 = two failures");
    if (natural === 20) pieces.push("regains 1 HP");
    if (event.is_stable) pieces.push("STABLE"); if (event.is_dead) pieces.push("DEAD");
    return pieces.join(" · ");
  }

  function format(event) {
    if (event.event_type === "attack") return formatAttack(event);
    if (event.event_type === "saving_throw") return formatSave(event);
    if (event.event_type === "death_save") return formatDeathSave(event);
    if (event.event_type === "healing" && event.target_name && event.hp_before != null && event.hp_after != null) return `${event.description} · ${event.target_name} HP ${event.hp_before}→${event.hp_after}`;
    return event.description || `${event.actor_name || "Arena"}: ${event.event_type}`;
  }

  window.IRON_PIT_BATTLE_LOG = { format, formatAttack, formatDeathSave, formatSave, rollLabel };
})();
