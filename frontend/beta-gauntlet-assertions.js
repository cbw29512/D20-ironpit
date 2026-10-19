(() => {
  "use strict";
  // Observed behavior is not the same as full RAW correctness or certified coverage.
  const families = Object.freeze({
    "melee attacks": (e) => e.event_type === "attack" && /melee/i.test(String(e.attack_kind || e.description || "")),
    "ranged attacks": (e) => e.event_type === "attack" && /ranged/i.test(String(e.attack_kind || e.description || "")),
    "spell effects": (e) => Boolean(e.concentration_started_effect_id) || /spell/i.test(String(e.animation || "")),
    "healing": (e) => e.event_type === "healing",
    "conditions applied": (e) => (e.applied_condition_ids || []).length > 0,
    "conditions removed": (e) => (e.removed_condition_ids || []).length > 0,
    "critical hits": (e) => e.event_type === "attack" && e.critical === true,
    "attack misses": (e) => e.event_type === "attack" && e.hit === false,
    "attack hits": (e) => e.event_type === "attack" && e.hit === true,
    "resources expended": (e) => typeof e.resource_remaining === "number",
    "damage components": (e) => (e.damage_components || []).length > 0,
    "saving throws": (e) => e.save_roll != null || e.saving_throw != null || e.saving_throw_roll != null,
    "ongoing effects": (e) => Boolean(e.concentration_started_effect_id) || /ongoing|start.turn|end.turn/i.test(String(e.description || "")),
    "buffs and defenses": (e) => /buff|shield|rage|defen[cs]e/i.test(String(e.animation || "")),
    "reactions": (e) => /reaction/i.test(String(e.animation || e.description || "")),
    "counters and mitigation": (e) => /counter|resist|immun|parry|redirect/i.test(String(e.animation || e.description || "")),
    "grapples and restraints": (e) => (e.applied_condition_ids || []).some((id) => ["grappled","restrained"].includes(id)),
    "prone": (e) => (e.applied_condition_ids || []).includes("prone"),
    "concentration": (e) => Boolean(e.concentration_started_effect_id),
    "movement and positioning": (e) => /mov|push|pull|teleport|disengage/i.test(String(e.animation || "")),
    "death and victory": (e) => e.event_type === "victory" || e.event_type === "draw",
  });
  function inspect(battle) {
    if (!battle || !Array.isArray(battle.events)) throw new Error("Battle event stream missing.");
    const names = new Set(), conditions = new Set(), features = new Set(), eventTypes = new Set();
    const samples = {};
    for (const event of battle.events) {
      if (!event || typeof event.event_type !== "string" || !Number.isInteger(event.round_number)
        || event.round_number < 0) throw Error("Malformed combat event.");
      eventTypes.add(event.event_type);
      if (event.feature_id) features.add(event.feature_id);
      for (const id of event.applied_condition_ids || []) conditions.add(id);
      for (const [family, predicate] of Object.entries(families)) {
        if (predicate(event)) {
          names.add(family);
          samples[family] ||= { round: event.round_number, feature: event.feature_id || null,
            event_type: event.event_type };
        }
      }
    }
    if (!battle.events.some((e) => e.event_type === "victory" || e.event_type === "draw")) {
      throw new Error("Battle did not emit terminal result event.");
    }
    return { families: [...names], conditions: [...conditions], features: [...features],
      event_types: [...eventTypes], samples };
  }
  function aggregate(rows) {
    const coverage = {};
    for (const family of Object.keys(families)) coverage[family] = { fights: 0, sample: null };
    for (const row of rows) {
      if (row.result !== "PASS" || !row.observed) continue;
      for (const family of row.observed.families) {
        coverage[family].fights++;
        coverage[family].sample ||= { preset: row.name, edition: row.edition, seed: row.seed,
          ...(row.observed.samples[family] || {}) };
      }
    }
    return coverage;
  }
  window.IRON_PIT_BETA_GAUNTLET_ASSERTIONS = { inspect, aggregate, families: Object.keys(families) };
})();
