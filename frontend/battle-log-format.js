(() => {
  "use strict";

  function rollLabel(roll) {
    if (!roll) return "no roll";
    const natural = roll.selected_roll;
    const mode = roll.mode === "advantage" ? "ADV" : roll.mode === "disadvantage" ? "DIS" : "d20";
    const pool = roll.rolls?.length > 1 ? ` [${roll.rolls.join(", ")}]` : "";
    const modifier = Number(roll.modifier || 0);
    const signed = modifier >= 0 ? `+${modifier}` : String(modifier);
    return `${mode}${pool} ${natural} ${signed} = ${roll.total}`;
  }

  function damageLabel(event) {
    if (!event.hit || !event.damage_roll) return "";
    const parts = (event.damage_components || []).map((part) =>
      `${part.applied_total ?? part.total} ${part.damage_type || "damage"}`,
    );
    return parts.length ? parts.join(" + ") : `${event.damage_roll.total} damage`;
  }

  function attackDeathLabel(event) {
    if (!event.hit || event.hp_before !== 0 || event.death_save_failures == null) return "";
    const added = event.critical ? 2 : 1;
    return `damage at 0 HP: +${added} Death failure${added === 1 ? "" : "s"} (now ${event.death_save_failures})`;
  }

  function formatAttack(event) {
    const natural = event.attack_roll?.selected_roll;
    const result = natural === 1 ? "NAT 1 · MISS" : event.critical ? "CRITICAL HIT" : event.hit ? "HIT" : "MISS";
    const pieces = [`${event.actor_name} → ${event.target_name}: ${result} with ${event.attack_name || event.weapon_id || "attack"}`];
    if (event.attack_roll) {
      const defense = event.target_ac == null ? "" : ` vs AC ${event.target_ac}`;
      pieces.push(`${rollLabel(event.attack_roll)}${defense}`);
    }
    const damage = damageLabel(event);
    if (damage) pieces.push(damage);
    if (event.hp_before != null && event.hp_after != null && event.hit) pieces.push(`HP ${event.hp_before}→${event.hp_after}`);
    const death = attackDeathLabel(event);
    if (death) pieces.push(death);
    if (event.is_dead) pieces.push("DEAD");
    if (event.applied_condition_ids?.length) pieces.push(event.applied_condition_ids.map((id) => id.toUpperCase()).join(", "));
    return pieces.join(" · ");
  }

  function counterLabel(name, before, after) {
    if (after == null) return "";
    return before == null ? `${name} ${after}` : `${name} ${before}→${after}`;
  }

  function formatDeathSave(event) {
    const natural = event.death_save_roll?.selected_roll;
    const tag = natural === 1 ? "NAT 1" : natural === 20 ? "NAT 20" : `d20 ${natural}`;
    const pieces = [
      `${event.actor_name}: Death Save ${tag}`,
      counterLabel("successes", event.death_save_successes_before, event.death_save_successes),
      counterLabel("failures", event.death_save_failures_before, event.death_save_failures),
    ].filter(Boolean);
    if (natural === 1) pieces.push("natural 1 = two failures");
    if (natural === 20) pieces.push("regains 1 HP");
    if (event.is_stable) pieces.push("STABLE");
    if (event.is_dead) pieces.push("DEAD");
    return pieces.join(" · ");
  }

  function format(event) {
    if (event.event_type === "attack") return formatAttack(event);
    if (event.event_type === "death_save") return formatDeathSave(event);
    if (event.event_type === "healing" && event.target_name && event.hp_before != null && event.hp_after != null) {
      return `${event.description} · ${event.target_name} HP ${event.hp_before}→${event.hp_after}`;
    }
    return event.description || `${event.actor_name || "Arena"}: ${event.event_type}`;
  }

  window.IRON_PIT_BATTLE_LOG = { format, formatAttack, formatDeathSave, rollLabel };
})();
