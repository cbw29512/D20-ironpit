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
      const tempLoss = Number.isFinite(event?.temporary_hp_before) && Number.isFinite(event?.temporary_hp_after)
        ? Math.max(0, event.temporary_hp_before - event.temporary_hp_after) : 0;
      if (hpLoss || tempLoss) return hpLoss + tempLoss;
      return Number.isFinite(event?.damage_roll?.total) ? Math.max(0, event.damage_roll.total) : 0;
    } catch (error) {
      console.error("Browser applied-damage measurement failed", { eventSequence: event?.sequence, error });
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
      if (appliedDamageTotal(triggeringEvent) <= 0) return { events: [], sequence };
      if (triggeringEvent.actor_id !== source.combatant_id) {
        throw new Error("Damage-trigger dispatch source must match the triggering event actor.");
      }
      const reactor = memberById(setup, triggeringEvent.target_id);
      if (!reactor) return { events: [], sequence };
      const reaction = R().resolve(sequence, round, reactor, source, setup, turnKey);
      if (!reaction) return { events: [], sequence };
      const events = [reaction];
      sequence += 1;
      const follow = resolve(sequence, round, reactor, reaction, setup, turnKey);
      events.push(...follow.events);
      return { events, sequence: follow.sequence };
    } catch (error) {
      console.error("Browser post-damage reaction dispatch failed", {
        source: source?.combatant_id, eventSequence: triggeringEvent?.sequence, error,
      });
      throw error;
    }
  }

  function append(events, sequence, round, source, event, setup, turnKey = null) {
    try {
      events.push(event);
      const reactions = resolve(sequence, round, source, event, setup, turnKey);
      events.push(...reactions.events);
      return reactions.sequence;
    } catch (error) {
      console.error("Browser event/reaction append failed", {
        source: source?.combatant_id, eventSequence: event?.sequence, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH = {
    appliedDamageTotal, append, memberById, resolve,
  };
})();
