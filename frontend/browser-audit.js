(() => {
  "use strict";

  const label = (id) => String(id || "effect").replaceAll("_", " ").replaceAll("-", " ");
  const step = (phase, kind, text) => ({ phase, kind, label: text });
  const signed = (value) => Number(value || 0) >= 0 ? `+${Number(value || 0)}` : String(value);

  function rollText(name, roll) {
    if (!roll) return `${name}: automatic failure; no die rolled`;
    const pool = `[${(roll.rolls || []).join(", ")}]`, selected = roll.selected_roll == null ? "" : `; selected ${roll.selected_roll}`;
    return `${name}: ${roll.notation} ${pool}${selected}; modifier ${signed(roll.modifier)}; total ${roll.total}`;
  }

  function revisionSteps(roll) {
    return (roll?.revisions || []).map((item) => {
      const source = label(item.source_effect_id), before = `[${item.original_rolls.join(", ")}]`, after = `[${item.replacement_rolls.join(", ")}]`;
      const index = item.replaced_die_index == null ? "" : `; replaced die #${item.replaced_die_index + 1}`;
      return step("reroll_or_replacement", "revision",
        `${source}: ${item.kind}${index}; original ${before} = ${item.original_total}; alternate ${after} = ${item.replacement_total}; accepted ${item.accepted}`);
    });
  }

  function rollSteps(event) {
    const out = [];
    const rows = [
      ["Attack roll", event.attack_roll], ["Saving throw", event.saving_throw_roll],
      ["Ability check", event.ability_check_roll], ["Death save", event.death_save_roll],
      ["Healing roll", event.healing_roll],
    ];
    for (const [name, roll] of rows) {
      if (!roll && !(name === "Saving throw" && event.event_type === "saving_throw")) continue;
      out.push(step("roll", "roll", rollText(name, roll)), ...revisionSteps(roll));
    }
    return out;
  }

  function checkSteps(event) {
    const out = [];
    if (event.attack_roll && event.target_ac != null) {
      out.push(step("hit_or_save_check", "check", `Attack total ${event.attack_roll.total} vs AC ${event.target_ac}: ${event.hit ? "hit" : "miss"}${event.critical ? "; critical" : ""}`));
    }
    if (event.event_type === "saving_throw" && event.save_dc != null) {
      const total = event.saving_throw_roll?.total;
      out.push(step("hit_or_save_check", "check", `${String(event.save_ability || "save").toUpperCase()} save ${total == null ? "automatic failure" : `${total} vs DC ${event.save_dc}`}: ${event.save_succeeded ? "success" : "failure"}`));
    }
    if (event.ability_check_roll && event.check_dc != null) {
      out.push(step("hit_or_save_check", "check", `${String(event.check_ability || "ability").toUpperCase()} check ${event.ability_check_roll.total} vs DC ${event.check_dc}: ${event.check_succeeded ? "success" : "failure"}`));
    }
    return out;
  }

  function damageSteps(event) {
    const out = [];
    for (const part of event.damage_components || []) {
      out.push(step("damage_roll", "damage", `${part.source}: ${part.notation} [${(part.rolls || []).join(", ")}] ${signed(part.modifier)} = ${part.total} ${part.damage_type}`));
      out.push(...revisionSteps(part));
      if (part.applied_total != null && part.applied_total !== part.total) {
        out.push(step("damage_applied", "defense", `${part.damage_type}: ${part.total} before defenses → ${part.applied_total} applied`));
      } else if (part.applied_total != null) {
        out.push(step("damage_applied", "damage", `${part.applied_total} ${part.damage_type} applied`));
      }
    }
    if (!out.length && event.damage_roll) out.push(step("damage_roll", "damage", rollText("Damage", event.damage_roll)));
    return out;
  }

  function stateSteps(event) {
    const out = [];
    if (event.temporary_hp_before != null && event.temporary_hp_after != null && event.temporary_hp_before !== event.temporary_hp_after) {
      out.push(step("state_change", "temp_hp", `Temporary HP ${event.temporary_hp_before} → ${event.temporary_hp_after}`));
    }
    if (event.hp_before != null && event.hp_after != null && event.hp_before !== event.hp_after) {
      out.push(step("state_change", "hp", `HP ${event.hp_before} → ${event.hp_after}`));
    }
    if (event.max_hp_before != null && event.max_hp_after != null && event.max_hp_before !== event.max_hp_after) {
      out.push(step("state_change", "max_hp", `Hit Point maximum ${event.max_hp_before} → ${event.max_hp_after}`));
    }
    for (const id of event.applied_condition_ids || []) out.push(step("state_change", "condition", `${label(id)} applied`));
    for (const id of event.removed_condition_ids || []) out.push(step("state_change", "condition", `${label(id)} ended`));
    if (event.concentration_started_effect_id) out.push(step("state_change", "concentration", `Concentration started: ${label(event.concentration_started_effect_id)}`));
    if (event.concentration_ended_effect_id) out.push(step("state_change", "concentration", `Concentration ended: ${label(event.concentration_ended_effect_id)}`));
    if (event.resource_remaining != null) out.push(step("resource_change", "resource", `${label(event.feature_id)} resource remaining: ${event.resource_remaining}`));
    if (event.is_stable) out.push(step("state_change", "outcome", "Target is stable at 0 HP"));
    if (event.is_dead) out.push(step("state_change", "outcome", "Target is dead"));
    return out;
  }

  function annotateEvent(event) {
    try {
      const phase = event.event_type === "initiative" ? "initiative" : event.round_number === 0 ? "precombat" : "action_selection";
      const name = event.attack_name || event.feature_id || event.event_type;
      const steps = [step(phase, "rule", `${event.actor_name || "Arena"}: ${label(name)}`), ...rollSteps(event), ...checkSteps(event), ...damageSteps(event), ...stateSteps(event)];
      if (event.event_type === "victory" || event.event_type === "draw") steps.push(step("combat_end", "outcome", event.description || event.event_type));
      return { ...event, audit: { schema_version: 1, steps } };
    } catch (error) {
      console.error("Iron Pit event audit annotation failed", error);
      throw error;
    }
  }

  function annotateBattle(battle) {
    try {
      if (!battle?.events) throw new Error("Resolved battle events are required for audit annotation.");
      return { ...battle, events: battle.events.map(annotateEvent) };
    } catch (error) {
      console.error("Iron Pit battle audit annotation failed", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_AUDIT = { annotateBattle, annotateEvent, revisionSteps, rollText };
})();