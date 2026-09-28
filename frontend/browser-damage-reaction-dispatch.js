(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_REACTIONS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_SOURCE_DAMAGE_TRIGGERS;

  function appliedDamageTotal(event) {
    try {
      const components = event?.damage_components || [];
      if (components.length && components.every((part) => Number.isFinite(part.applied_total))) {
        return components.reduce((sum, part) => sum + Math.max(0, part.applied_total), 0);
      }
      const hpKnown = Number.isFinite(event?.hp_before) && Number.isFinite(event?.hp_after);
      const tempKnown = Number.isFinite(event?.temporary_hp_before)
        && Number.isFinite(event?.temporary_hp_after);
      const hpLoss = hpKnown ? Math.max(0, event.hp_before - event.hp_after) : 0;
      const tempLoss = tempKnown
        ? Math.max(0, event.temporary_hp_before - event.temporary_hp_after) : 0;
      if (hpKnown || tempKnown) return hpLoss + tempLoss;
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

  function resolveSourceZeroHpTrigger(sequence, round, source, triggeringEvent, setup) {
    const rule = source?.state?.template?.source_reduces_hostile_to_zero_hp_temporary_hp;
    if (!rule) return { events: [], sequence };
    if (triggeringEvent.actor_id !== source.combatant_id) {
      throw new Error("Zero-HP trigger source must match the triggering event actor.");
    }
    const target = memberById(setup, triggeringEvent.target_id);
    if (!target || target.combatant_id === source.combatant_id || target.side === source.side) {
      return { events: [], sequence };
    }
    if (!Number.isFinite(triggeringEvent.hp_before) || !Number.isFinite(triggeringEvent.hp_after)) {
      return { events: [], sequence };
    }
    if (triggeringEvent.hp_before <= 0 || triggeringEvent.hp_after !== 0) {
      return { events: [], sequence };
    }
    const scores = source.state.template.ability_scores;
    const level = source.state.template.level;
    if (!scores || !Number.isInteger(level)) {
      throw new Error("Zero-HP Temporary HP trigger requires certified ability scores and level.");
    }
    const score = scores[rule.ability];
    if (!Number.isFinite(score)) throw new Error("Zero-HP Temporary HP trigger ability score is unavailable.");
    const abilityModifier = Math.floor((score - 10) / 2);
    const amount = Math.max(rule.minimum ?? 1, (rule.flat_bonus || 0) + (rule.per_level || 0) * level + abilityModifier);
    const before = source.state.temporary_hp || 0;
    const stateRuntime = S();
    if (!stateRuntime?.grantTemporaryHp) throw new Error("Browser Temporary HP runtime is not loaded.");
    const after = stateRuntime.grantTemporaryHp(source.state, amount);
    return {
      events: [{
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: source.combatant_id,
        actor_name: source.state.template.name,
        target_id: source.combatant_id,
        target_name: source.state.template.name,
        hp_before: source.state.current_hp,
        hp_after: source.state.current_hp,
        temporary_hp_before: before,
        temporary_hp_after: after,
        feature_id: rule.source_id,
        animation: "feature",
        description: `${source.state.template.name} gains ${amount} Temporary HP from ${rule.source_name} after reducing a hostile creature to 0 HP.`,
      }],
      sequence: sequence + 1,
    };
  }

  function resolve(sequence, round, source, triggeringEvent, setup, turnKey = null) {
    try {
      if (triggeringEvent.actor_id !== source.combatant_id) {
        throw new Error("Damage reaction source must match the triggering event actor.");
      }
      const sourceTrigger = resolveSourceZeroHpTrigger(sequence, round, source, triggeringEvent, setup);
      sequence = sourceTrigger.sequence;
      const appliedDamage = appliedDamageTotal(triggeringEvent);
      const damageTrigger = T()?.resolve(sequence, round, source, triggeringEvent, appliedDamage)
        || { events: [], sequence };
      sequence = damageTrigger.sequence;
      sourceTrigger.events.push(...damageTrigger.events);
      if (appliedDamage <= 0) return sourceTrigger;
      const reactor = memberById(setup, triggeringEvent.target_id);
      if (!reactor || reactor.combatant_id === source.combatant_id) {
        return sourceTrigger;
      }
      const runtime = R();
      if (!runtime) {
        if (reactor.state.template.damage_reaction_attack) {
          throw new Error("Damage reaction runtime is not loaded for a declared reaction.");
        }
        return sourceTrigger;
      }
      const reaction = runtime.resolve(
        sequence, round, reactor, source, setup, appliedDamage, turnKey,
      );
      if (!reaction) return sourceTrigger;
      const events = [...sourceTrigger.events, reaction];
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
    appliedDamageTotal, chain, memberById, resolve, resolveSourceZeroHpTrigger,
  };
})();