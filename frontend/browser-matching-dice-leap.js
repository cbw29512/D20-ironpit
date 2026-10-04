(() => {
  "use strict";

  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const AR = () => window.IRON_PIT_BROWSER_SPELL_ATTACK;
  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const GB = () => window.IRON_PIT_BROWSER_GRID_BARRIERS;

  function matchingFaces(event, spell) {
    try {
      if (!event?.hit) return false;
      const own = (event.damage_components || []).find((part) => part.source === spell.name);
      if (!own || !Array.isArray(own.rolls) || own.rolls.length < 2) return false;
      const counts = {};
      for (const face of own.rolls) counts[face] = (counts[face] || 0) + 1;
      return Object.values(counts).some((count) => count >= 2);
    } catch (error) {
      console.error("Failed matching-dice check", { spell: spell?.id, error });
      throw error;
    }
  }

  function chooseTarget(caster, origin, setup, rangeFt, excludedIds) {
    try {
      const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
      return (enemies || []).find((candidate) => {
        if (excludedIds.has(candidate.combatant_id)) return false;
        if (!candidate.state.is_alive || candidate.state.is_dead || candidate.state.current_hp <= 0) return false;
        if (ST().distance(origin, candidate) > rangeFt) return false;
        if (GB()?.clearBetweenMembers && !GB().clearBetweenMembers(origin, candidate, setup)) return false;
        return true;
      }) || null;
    } catch (error) {
      console.error("Failed matching-dice leap target choice", { origin: origin?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, caster, origin, lastEvent, spell, setup, turnKey, options = {}) {
    try {
      const rangeFt = spell.matchingDiceLeapRangeFt || 0;
      if (rangeFt <= 0) return { events: [], sequence };
      const slotLevel = options.slotLevel ?? 0;
      const maxLeaps = slotLevel > 0 ? slotLevel : spell.level;
      const excluded = new Set(lastEvent.target_id ? [lastEvent.target_id] : []);
      const events = [];
      let currentOrigin = origin;
      let currentEvent = lastEvent;
      let leaps = 0;
      while (leaps < maxLeaps) {
        if (!matchingFaces(currentEvent, spell)) break;
        const target = chooseTarget(caster, currentOrigin, setup, rangeFt, excluded);
        if (!target) break;
        const event = AR().resolve(sequence, round, caster, target, spell, setup, turnKey, {
          rangeModifier: options.rangeModifier || null,
          castSlotLevel: spell.level > 0 ? slotLevel : null,
          spendCastCosts: false,
          skipRangeCheck: true,
        });
        sequence += 1;
        if (DR()) {
          const chain = DR().chain(sequence, round, caster, event, setup, turnKey);
          events.push(...chain.events);
          sequence = chain.sequence;
        } else {
          events.push(event);
        }
        leaps += 1;
        excluded.add(target.combatant_id);
        currentOrigin = target;
        currentEvent = event;
      }
      return { events, sequence };
    } catch (error) {
      console.error("Matching-dice leap failed", { caster: caster?.combatant_id, spell: spell?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MATCHING_DICE_LEAP = { matchingFaces, chooseTarget, resolve };
})();
