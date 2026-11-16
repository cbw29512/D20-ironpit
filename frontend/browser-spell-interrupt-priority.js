(() => {
  "use strict";

  function dispatch(sequence, round, caster, setup, initiativeOrder,
    reactionsById, incomingName, incomingLevel, isSpellCast) {
    try {
      const members = new Map(
        [...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]),
      );
      if (!Array.isArray(initiativeOrder) || !initiativeOrder.length
        || initiativeOrder.length !== members.size
        || new Set(initiativeOrder).size !== members.size
        || initiativeOrder.some((id) => !members.has(id))) {
        throw new Error("Reaction priority requires the complete resolved initiative order.");
      }
      if (Object.keys(reactionsById || {}).some((id) => !members.has(id))) {
        throw new Error("Reaction source references a missing combatant.");
      }
      if (typeof isSpellCast !== "boolean")
        throw new Error("Spell-casting provenance must be explicitly typed.");
      if (!isSpellCast) return {events: [], stopped: false, sequence};

      const runtime = window.IRON_PIT_BROWSER_SPELL_INTERRUPT;
      if (!runtime?.legal || !runtime?.resolve)
        throw new Error("Universal spell-interruption reaction runtime is missing.");
      const events = [];
      for (const id of initiativeOrder) {
        const actor = members.get(id);
        for (const action of (reactionsById?.[id] || [])) {
          if (!action || !Number.isInteger(action.printedLevel)
            || action.trigger !== "visible_spell_cast") {
            throw new Error("Reaction entry must declare a source-proven spell trigger.");
          }
          if (!runtime.legal(actor, caster, action, incomingLevel, true)) continue;
          const [event, interrupted] = runtime.resolve(
            sequence, round, actor, caster, setup, action,
            incomingName, incomingLevel, true,
          );
          events.push(event);
          sequence++;
          if (interrupted) return {events, stopped: true, sequence};
        }
      }
      return {events, stopped: false, sequence};
    } catch (error) {
      console.error("Initiative-ordered spell interruption failed", {
        casterId: caster?.combatant_id, error,
      });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_SPELL_INTERRUPT_PRIORITY = {dispatch};
})();
