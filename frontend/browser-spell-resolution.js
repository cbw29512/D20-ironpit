(() => {
  "use strict";

  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const SC = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const CONC = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const SM = () => window.IRON_PIT_BROWSER_SPELL_MODIFIERS;
  const CE = () => window.IRON_PIT_BROWSER_SPELL_CAST_EFFECTS;
  const H = () => window.IRON_PIT_BROWSER_SPELL_SAVE_DISADVANTAGE;
  const R = () => window.IRON_PIT_BROWSER_DAMAGING_ACTION_RIDERS;

  const FX = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION_EFFECTS;

  function resolve(sequence, round, caster, setup, choice, turnKey) {
    try {
      const spell = choice.action;
      FX().scaledSpell(spell, choice.slotLevel);
      if (spell.actionCost === "reaction") throw new Error("Reaction spells require their trigger window.");
      if (!E().available(caster.state, spell.actionCost)) throw new Error(`${spell.actionCost} is unavailable for ${spell.name}.`);

      let remaining = null;
      if (choice.alternateCast) {
        const grant = choice.alternateCast;
        if (grant.cast_level !== choice.slotLevel) {
          throw new Error("Alternate spell cast level does not match the selected cast level.");
        }
        if (grant.resource_id) {
          const current = caster.state.resources?.[grant.resource_id] || 0;
          const cost = grant.resource_cost || 1;
          if (current < cost) throw new Error(`Insufficient ${grant.resource_id} for ${grant.source_name}.`);
          caster.state.resources[grant.resource_id] = current - cost;
          remaining = caster.state.resources[grant.resource_id];
        }
      } else if (choice.slotLevel > 0) {
        const resourceId = `spell-slot-${choice.slotLevel}`;
        if (!(caster.state.resources?.[resourceId] > 0)) throw new Error(`No level ${choice.slotLevel} spell slot remains.`);
        SC().markSlotSpellCast(caster.state, turnKey);
        caster.state.resources[resourceId] -= 1;
        remaining = caster.state.resources[resourceId];
      }
      E().spend(caster.state, spell.actionCost);
      const rangeRemaining = choice.rangeModifier
        ? (P()?.spendRangeModifier
          ? P().spendRangeModifier(caster.state, choice.rangeModifier)
          : (() => {
              const current = caster.state.resources?.[choice.rangeModifier.resourceId] || 0;
              const cost = choice.rangeModifier.resourceCost || 1;
              if (current < cost) throw new Error(`Insufficient ${choice.rangeModifier.resourceId} for ${choice.rangeModifier.name}.`);
              caster.state.resources[choice.rangeModifier.resourceId] = current - cost;
              return caster.state.resources[choice.rangeModifier.resourceId];
            })())
        : null;
      window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.removeOwnerAttackEnding(caster.state);
      CE()?.applyTimedResistance(caster, FX().scaledSpell(spell, choice.slotLevel), round);

      const allStates = [...setup.heroes, ...setup.monsters].map((member) => member.state);
      if (spell.concentration) {
        if (!CONC()) throw new Error("Browser Concentration runtime is not loaded.");
        const durationRounds = (spell.durationMinutes || 0) * 10;
        if (durationRounds <= 0) throw new Error("Concentration save spell requires a positive duration.");
        CONC().start(
          caster.state, caster.combatant_id, spell.id, round, allStates,
          round + durationRounds, choice.slotLevel > 0 ? choice.slotLevel : null,
        );
      }

      const placement = choice.placement;
      const detail = placement
        ? ` Area covers ${placement.enemyIds.length} enemies, ${placement.friendlyIds.length} unprotected allies, and ${(placement.protectedFriendlyIds || []).length} protected allies.`
        : "";
      const slotText = choice.alternateCast
        ? choice.alternateCast.source_name
        : (choice.slotLevel === 0 ? "cantrip" : `level ${choice.slotLevel} slot`);
      const events = [];
      if (choice.rangeModifier) {
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: caster.combatant_id, actor_name: caster.state.template.name,
          feature_id: choice.rangeModifier.id, resource_remaining: rangeRemaining,
          animation: "spell-range",
          description: `${caster.state.template.name} uses ${choice.rangeModifier.name} to extend ${spell.name}'s range.`,
        });
      }
      events.push({
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: caster.combatant_id, actor_name: caster.state.template.name,
        feature_id: spell.id, resource_remaining: remaining,
        animation: spell.animation || "spell-save",
        description: `${caster.state.template.name} casts ${spell.name} using a ${slotText}.${detail}`,
      });

      const effect = FX().resolveEffect(sequence, round, caster, setup, choice, turnKey);
      events.push(...effect.events);
      sequence = effect.sequence;
      const riderEvent = R()?.resolve?.(
        sequence, round, caster, setup, spell.id, events,
      ) || null;
      if (riderEvent) {
        events.push(riderEvent);
        sequence += 1;
      }
      if (choice.damageMaximizer) {
        const followUp = C().resolveDamageMaximizerAfterCast(
          sequence, round, caster, setup, choice.damageMaximizer, choice.slotLevel,
        );
        events.push(...followUp.events);
        sequence = followUp.sequence;
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser save-spell resolution failed", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_RESOLUTION = {
    resolve,
    resolveEffect: FX().resolveEffect,
    saveAction: FX().saveAction,
  };
})();
