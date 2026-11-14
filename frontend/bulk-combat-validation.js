(() => {
  "use strict";
  // Auditing is read-only. Per-fight mutable engine state and source templates
  // remain owned exclusively by the canonical combat resolver.
  function inspect(battle, originals = [], bagActorId = null) {
    try {
      const problems = [];
      const events = battle?.events;
      if (!Array.isArray(events) || !events.length)
        problems.push("no_combat_events");
      if (!["heroes_win", "monsters_win", "draw"].includes(battle?.outcome))
        problems.push("invalid_outcome");
      if (events?.some(event => event.event_type === "movement"))
        problems.push("forbidden_tactical_movement");
      for (const [card, original] of originals)
        if (JSON.stringify(card) !== original)
          problems.push("source_card_mutation");
      if (bagActorId) {
        if (!battle?.setup || ![...battle.setup.heroes, ...battle.setup.monsters]
          .some(member => member.combatant_id === bagActorId))
          problems.push("punching_bag_actor_missing");
        if (events?.some(event => event.actor_id === bagActorId &&
          ((event.damage_roll?.total || 0) > 0 ||
            (event.damage_components || []).some(part => (part.applied_total || 0) > 0))))
          problems.push("punching_bag_dealt_damage");
      }
      return problems;
    } catch (error) {
      console.error("Bulk fight read-only outcome inspection failed", {bagActorId, error});
      throw error;
    }
  }

  function abilityEvidence(source, events, actorId) {
    try {
      const audit = window.IRON_PIT_TEST_BAG_COVERAGE?.audit;
      if (!audit) throw new Error("Universal source ability coverage recorder is missing.");
      return audit(source, events, actorId);
    } catch (error) {
      console.error("Could not audit observed source capabilities", {actorId, error});
      throw error;
    }
  }

  window.IRON_PIT_BULK_COMBAT_VALIDATION = {inspect, abilityEvidence};
})();