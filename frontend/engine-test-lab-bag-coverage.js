(() => {
  "use strict";
  // Expected abilities come from the already compiled immutable card;
  // observed abilities require actual actor-owned combat events. No names
  // are used for combat dispatch, only for audit/display reconciliation.
  const ACTIVE_FIELDS = [
    "attacks", "saving_throw_actions", "spell_attack_actions",
    "auto_hit_spell_actions", "healing_actions", "spell_actions",
    "spell_save_actions", "hit_point_pool_spell_actions",
    "bonus_action_attacks", "bonus_action_saving_throw_actions",
    "reaction_actions", "legendary_actions", "buff_actions",
    "defensive_spell_actions", "innate_actions", "special_actions",
    "attack_action", "bonus_action", "reaction_action",
  ];
  const SOURCE_FIELDS = [
    "source_trait_names", "source_reaction_names",
    "source_legendary_action_names", "source_bonus_action_names",
    "source_limited_use_names",
  ];

  function declared(card) {
    try {
      if (!card || typeof card !== "object")
        throw new Error("Ability audit requires an immutable source card.");
      const out = new Map();
      const add = (category, item, sourceOnly = false) => {
        if (!item) return;
        const id = typeof item === "string" ? item
          : item.id || item.name || item.sourceName;
        const name = typeof item === "string" ? item : item.name || item.sourceName || id;
        if (typeof id !== "string" || !id) return;
        const key = `${category}:${id}`;
        if (!out.has(key)) out.set(key, {category, id, name,
          source_only: sourceOnly});
      };
      for (const field of ACTIVE_FIELDS) {
        const rows = card[field] ? [].concat(card[field]) : [];
        for (const item of rows) add(field, item);
      }
      for (const field of SOURCE_FIELDS) {
        const rows = Array.isArray(card[field]) ? card[field] : [];
        for (const item of rows) add(field, item, true);
      }
      for (const trait of card.traits || []) add("traits", trait);
      for (const rule of card.recharge_rules || [])
        add("recharge_rules", rule.resourceId || rule.resource_id);
      return [...out.values()];
    } catch (error) {
      console.error("Could not enumerate compiled card abilities", {id: card?.id, error});
      throw error;
    }
  }

  function audit(card, events, actorId) {
    try {
      if (!Array.isArray(events) || !actorId)
        throw new Error("Ability audit requires real events and an actor.");
      const emitted = new Set();
      const event_types = {};
      const branches = {};
      const add = id => {
        if (typeof id === "string" && id) emitted.add(id.toLowerCase());
      };
      for (const event of events) {
        if (event.actor_id !== actorId) continue;
        const type = event.event_type || "unknown";
        event_types[type] = (event_types[type] || 0) + 1;
        for (const key of ["feature_id", "weapon_id", "attack_id", "action_id",
          "spell_id", "attack_name", "spell_name", "feature_name"]) add(event[key]);
        if (type === "attack") {
          const outcome = event.hit === true ? "hit" :
            event.hit === false ? "miss" : "unknown";
          const name = `attack_${outcome}`;
          branches[name] = (branches[name] || 0) + 1;
          if (event.critical === true)
            branches.attack_critical = (branches.attack_critical || 0) + 1;
        }
        if (Array.isArray(event.applied_condition_ids) &&
            event.applied_condition_ids.length)
          branches.applied_conditions = (branches.applied_conditions || 0) + 1;
      }
      const expected = declared(card);
      const exercised = expected.filter(item =>
        emitted.has(item.id.toLowerCase()) ||
        (!item.source_only && emitted.has(item.name.toLowerCase())));
      const unobserved = expected.filter(item => !exercised.includes(item));
      return {
        declared_count: expected.length,
        exercised_count: exercised.length,
        not_observed_count: unobserved.length,
        exercised, not_observed: unobserved, branches, event_types,
        // An unobserved action is not a certified failure unless the test
        // explicitly forced that action and checked the result.
        coverage_note: "Observed combat only: untriggered abilities remain unverified.",
      };
    } catch (error) {
      console.error("Punching Bag ability evidence audit failed", {actorId, error});
      throw error;
    }
  }
  window.IRON_PIT_TEST_BAG_COVERAGE = {declared, audit};
})();
