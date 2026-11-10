(() => {
  "use strict";

  // Shared timed-condition capacity, not monster-specific Charm behavior.
  function enforce(actor, newest, actionId, effectId, maximum, setup) {
    try {
      if (!Number.isInteger(maximum) || maximum < 1 || maximum > 20) {
        throw new Error("Source-target capacity must be between 1 and 20.");
      }
      if (!setup) throw new Error("Source-target capacity requires encounter setup.");
      const members = [...(setup.heroes || []), ...(setup.monsters || [])];
      if (!members.includes(actor) || !members.includes(newest)) {
        throw new Error("Source-target capacity members must belong to the encounter.");
      }
      const owned = (member) => (member.state.timed_effects || []).find((effect) =>
        effect.effect_id === effectId && effect.source_id === actor.combatant_id
          && effect.source_effect_id === actionId,
      );
      const active = members.map((member) => ({ member, effect: owned(member) }))
        .filter((item) => Boolean(item.effect));
      if (!owned(newest)) {
        throw new Error("Source-target capacity requires an applied effect.");
      }
      if (active.length <= maximum) return [];
      const others = active.filter((item) => item.member !== newest)
        .sort((a, b) => ((a.effect.applied_round || 0) - (b.effect.applied_round || 0))
          || String(a.member.combatant_id).localeCompare(String(b.member.combatant_id)));
      const timed = window.IRON_PIT_BROWSER_TIMED;
      const immunity = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS;
      if (!timed?.removeGroup || !immunity?.grantImmunity) {
        throw new Error("Source-target capacity requires shared timed lifecycle.");
      }
      const expired = [];
      for (const { member, effect } of others.slice(0, active.length - maximum)) {
        timed.removeGroup(member.state, effect);
        if (owned(member)) throw new Error("Source-owned control was not released.");
        // An overlapping condition from a different owner may remain active.
        // The removed instance still grants its source-scoped on-end immunity.
        if (effect.source_effect_immunity_on_end
          && !immunity.isImmune(member, { id: actionId }, actor.combatant_id)) {
          immunity.grantImmunity(
            member.state, actionId, actor.combatant_id,
            member.state.current_round || 1,
            { sourceIsMagical: Boolean(effect.source_is_magical) },
          );
        }
        expired.push(member.combatant_id);
      }
      return expired;
    } catch (error) {
      console.error("Source-target capacity resolution failed.", { actionId, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SOURCE_TARGET_CAPACITY = { enforce };
})();
