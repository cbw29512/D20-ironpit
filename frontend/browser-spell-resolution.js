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

  function scaledSpell(action, slotLevel) {
    const policy = P();
    if (policy?.scaledSpell) return policy.scaledSpell(action, slotLevel);
    if ((action.level === 0 && slotLevel === 0) || slotLevel === action.level) return action;
    throw new Error("Browser spell policy runtime is required for higher-slot save-spell scaling.");
  }

  function saveAction(choice) {
    try {
      const spell = scaledSpell(choice.action, choice.slotLevel);
      return {
        id: spell.id, name: spell.name, saveAbility: spell.saveAbility, dc: spell.dc,
        range: spell.range + (spell.areaRadius || 0),
        damageDiceCount: spell.damageDiceCount,
        damageDiceSize: spell.damageDiceSize, damageBonus: spell.damageBonus || 0,
        damageType: spell.damageType, successDamage: spell.successDamage || "none",
        damageComponents: (spell.damageComponents || []).map((item) => ({ ...item })),
        magicalEffect: true, effectTags: [...(spell.effectTags || [])],
        area: spell.area || null,
        animation: spell.animation || "spell-save",
      };
    } catch (error) {
      console.error("Browser save-spell compilation failed", { spell: choice?.action?.id, error });
      throw error;
    }
  }

  function resolve(sequence, round, caster, setup, choice, turnKey) {
    try {
      const spell = choice.action;
      scaledSpell(spell, choice.slotLevel);
      if (spell.actionCost === "reaction") throw new Error("Reaction spells require their trigger window.");
      if (!E().available(caster.state, spell.actionCost)) throw new Error(`${spell.actionCost} is unavailable for ${spell.name}.`);

      let remaining = null;
      if (choice.slotLevel > 0) {
        const resourceId = `spell-slot-${choice.slotLevel}`;
        if (!(caster.state.resources?.[resourceId] > 0)) throw new Error(`No level ${choice.slotLevel} spell slot remains.`);
        SC().markSlotSpellCast(caster.state, turnKey);
        caster.state.resources[resourceId] -= 1;
        remaining = caster.state.resources[resourceId];
      }
      E().spend(caster.state, spell.actionCost);
      window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.removeOwnerAttackEnding(caster.state);

      const allStates = [...setup.heroes, ...setup.monsters].map((member) => member.state);
      if (spell.concentration) {
        if (!CONC()) throw new Error("Browser Concentration runtime is not loaded.");
        const durationRounds = (spell.durationMinutes || 0) * 10;
        if (durationRounds <= 0) throw new Error("Concentration save spell requires a positive duration.");
        CONC().start(caster.state, caster.combatant_id, spell.id, round, allStates, round + durationRounds, choice.slotLevel > 0 ? choice.slotLevel : null);
      }

      const placement = choice.placement;
      const detail = placement
        ? ` Area covers ${placement.enemyIds.length} enemies and ${placement.friendlyIds.length} unprotected allies.`
        : "";
      const slotText = choice.slotLevel === 0 ? "cantrip" : `level ${choice.slotLevel} slot`;
      const events = [{
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: caster.combatant_id, actor_name: caster.state.template.name,
        feature_id: spell.id, resource_remaining: remaining, animation: spell.animation || "spell-save",
        description: `${caster.state.template.name} casts ${spell.name} using a ${slotText}.${detail}`,
      }];

      const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
      const action = saveAction(choice);
      let sharedDamageRolls = null;
      for (const targetId of choice.targetIds) {
        const target = members.get(targetId);
        const ward = (spell.areaRadius || spell.area) ? null : (window.IRON_PIT_BROWSER_TARGETING_WARDS?.check(caster, target) || null);
        if (ward && !ward.succeeded) {
          events.push(window.IRON_PIT_BROWSER_TARGETING_WARDS.blocked(sequence++, round, caster, target, spell.name, ward));
          continue;
        }
        const event = V().resolveAction(
          sequence, round, caster, target, action, placement ? 0 : S().distance(caster, target),
          { spendAction: false, sharedDamageRolls, spellEffect: true, setup },
        );
        sequence += 1;
        if (ward) window.IRON_PIT_BROWSER_TARGETING_WARDS.annotate(event, ward, caster.state.template.name);
        if (event.save_succeeded === false && (spell.failedSaveModifierEffects || []).length) {
          if (!SM() || !M()) throw new Error("Failed-save spell modifiers require browser modifier runtimes.");
          spell.failedSaveModifierEffects.forEach((effect, index) => {
            M().add(target.state, SM().build(
              caster.combatant_id, target.combatant_id, spell, effect, index, round,
            ));
          });
        }
        const chain = DR() ? DR().chain(sequence, round, caster, event, setup, turnKey)
          : { events: [event], sequence };
        events.push(...chain.events); sequence = chain.sequence;
        if (sharedDamageRolls == null && event.damage_components?.length) {
          sharedDamageRolls = action.damageComponents?.length
            ? event.damage_components.map((component) => [...component.rolls])
            : [...event.damage_components[0].rolls];
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser save-spell resolution failed", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_RESOLUTION = { resolve, saveAction };
})();