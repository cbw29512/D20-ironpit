(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_REACTIONS;

  function appliedDamageTotal(event) {
    try {
      const components = event?.damage_components || [];
      if (components.length && components.every((part) => Number.isFinite(part.applied_total))) {
        return components.reduce((sum, part) => sum + Math.max(0, part.applied_total), 0);
      }
      const hpLoss = Number.isFinite(event?.hp_before) && Number.isFinite(event?.hp_after)
        ? Math.max(0, event.hp_before - event.hp_after) : 0;
      const tempLoss = Number.isFinite(event?.temporary_hp_before)
        && Number.isFinite(event?.temporary_hp_after)
        ? Math.max(0, event.temporary_hp_before - event.temporary_hp_after) : 0;
      if (hpLoss || tempLoss) return hpLoss + tempLoss;
      return Number.isFinite(event?.damage_roll?.total) ? Math.max(0, event.damage_roll.total) : 0;
    } catch (error) {
      console.error("Browser applied-damage measurement failed", {
        eventSequence: event?.sequence, error,
      });
      throw error;
    }
  }

  function memberById(setup, id) {
    if (!id) return null;
    return [...(setup?.heroes || []), ...(setup?.monsters || [])]
      .find((member) => member.combatant_id === id) || null;
  }

  function resolve(sequence, round, source, triggeringEvent, setup, turnKey = null) {
    try {
      const appliedDamage = appliedDamageTotal(triggeringEvent);
      if (appliedDamage <= 0) return { events: [], sequence };
      if (triggeringEvent.actor_id !== source.combatant_id) {
        throw new Error("Damage reaction source must match the triggering event actor.");
      }
      const reactor = memberById(setup, triggeringEvent.target_id);
      if (!reactor || reactor.combatant_id === source.combatant_id) {
        return { events: [], sequence };
      }
      const runtime = R();
      if (!runtime) {
        if (reactor.state.template.damage_reaction_attack) {
          throw new Error("Damage reaction runtime is not loaded for a declared reaction.");
        }
        return { events: [], sequence };
      }
      const reaction = runtime.resolve(
        sequence, round, reactor, source, setup, appliedDamage, turnKey,
      );
      if (!reaction) return { events: [], sequence };
      const events = [reaction];
      const nested = resolve(sequence + 1, round, reactor, reaction, setup, turnKey);
      events.push(...nested.events);
      return { events, sequence: nested.sequence };
    } catch (error) {
      console.error("Browser post-damage reaction dispatch failed", {
        source: source?.combatant_id, eventSequence: triggeringEvent?.sequence, error,
      });
      throw error;
    }
  }

  function chain(nextSequence, round, source, event, setup, turnKey = null) {
    const reactions = resolve(nextSequence, round, source, event, setup, turnKey);
    return { events: [event, ...reactions.events], sequence: reactions.sequence };
  }

  window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH = {
    appliedDamageTotal, chain, memberById, resolve,
  };
})();