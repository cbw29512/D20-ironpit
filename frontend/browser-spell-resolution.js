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
  const F = () => window.IRON_PIT_BROWSER_SPELL_FEATURES;

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

  function resolveEffect(sequence, round, caster, setup, choice, turnKey) {
    try {
      const spell = scaledSpell(choice.action, choice.slotLevel);
      const placement = choice.placement;
      const members = new Map([...setup.heroes, ...setup.monsters]
        .map((member) => [member.combatant_id, member]));
      const action = saveAction(choice);
      const events = [];
      let sharedDamageRolls = choice.maximizeDamage ? F().maximizedRolls(spell) : null;
      let saveDisadvantage = H()?.choose(caster.state) || null;

      for (const targetId of choice.targetIds) {
        const target = members.get(targetId);
        if (!target) throw new Error(`Save-spell target ${targetId} is unavailable.`);
        const ward = (spell.areaRadius || spell.area)
          ? null
          : (window.IRON_PIT_BROWSER_TARGETING_WARDS?.check(caster, target) || null);
        if (ward && !ward.succeeded) {
          events.push(window.IRON_PIT_BROWSER_TARGETING_WARDS
            .blocked(sequence++, round, caster, target, spell.name, ward));
          continue;
        }
        let saveDisadvantageSources = [];
        let modifierRemaining = null;
        if (saveDisadvantage) {
          modifierRemaining = H().spend(caster.state, saveDisadvantage);
          saveDisadvantageSources = [saveDisadvantage.name];
          saveDisadvantage = null;
        }
        const event = V().resolveAction(
          sequence, round, caster, target, action,
          placement ? 0 : S().distance(caster, target),
          {
            spendAction: false, sharedDamageRolls, spellEffect: true, setup,
            saveDisadvantageSources, resourceRemaining: modifierRemaining,
          },
        );
        sequence += 1;
        if (ward) {
          window.IRON_PIT_BROWSER_TARGETING_WARDS
            .annotate(event, ward, caster.state.template.name);
        }
        if (event.save_succeeded === false && (spell.failedSaveModifierEffects || []).length) {
          if (!SM() || !M()) throw new Error("Failed-save spell modifiers require browser modifier runtimes.");
          spell.failedSaveModifierEffects.forEach((effect, index) => {
            M().add(target.state, SM().build(
              caster.combatant_id, target.combatant_id, spell, effect, index, round,
            ));
          });
        }
        const chain = DR()
          ? DR().chain(sequence, round, caster, event, setup, turnKey)
          : { events: [event], sequence };
        events.push(...chain.events);
        sequence = chain.sequence;
        if (sharedDamageRolls == null && event.damage_components?.length) {
          sharedDamageRolls = action.damageComponents?.length
            ? event.damage_components.map((component) => [...component.rolls])
            : [...event.damage_components[0].rolls];
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser save-spell effect resolution failed", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, caster, setup, choice, turnKey) {
    try {
      const spell = choice.action;
      scaledSpell(spell, choice.slotLevel);
      if (spell.actionCost === "reaction") throw new Error("Reaction spells require their trigger window.");
      if (!E().available(caster.state, spell.actionCost)) throw new Error(`${spell.actionCost} is unavailable for ${spell.name}.`);

      let remaining = null, castGrant = null;
      if (choice.slotLevel > 0) {
        const spent = F().spendGrant(caster.state, spell, choice.slotLevel);
        castGrant = spent.grant;
        if (castGrant) {
          remaining = spent.remaining;
        } else {
          const resourceId = `spell-slot-${choice.slotLevel}`;
          if (!(caster.state.resources?.[resourceId] > 0)) throw new Error(`No level ${choice.slotLevel} spell slot remains.`);
          SC().markSlotSpellCast(caster.state, turnKey);
          caster.state.resources[resourceId] -= 1;
          remaining = caster.state.resources[resourceId];
        }
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
      CE()?.applyTimedResistance(caster, scaledSpell(spell, choice.slotLevel), round);

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
        ? ` Area covers ${placement.enemyIds.length} enemies and ${placement.friendlyIds.length} unprotected allies.`
        : "";
      const slotText = castGrant ? `${castGrant.source_name} free cast` : (choice.slotLevel === 0 ? "cantrip" : `level ${choice.slotLevel} slot`);
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

      const effect = resolveEffect(sequence, round, caster, setup, choice, turnKey);
      events.push(...effect.events);
      sequence = effect.sequence;
      if (choice.maximizeDamage) {
        const cost = F().applyMaximizerCost(caster, spell, setup);
        if (cost) {
          events.push({
            sequence: sequence++, round_number: round, event_type: "feature",
            actor_id: caster.combatant_id, actor_name: caster.state.template.name,
            target_id: caster.combatant_id, target_name: caster.state.template.name,
            feature_id: cost.grant.source_id,
            damage_roll: { notation: `${cost.count}d${cost.grant.self_damage_die_size || 12}`,
              rolls: cost.rolls, modifier: 0, total: cost.total },
            damage_components: [{
              source: cost.grant.source_name,
              notation: `${cost.count}d${cost.grant.self_damage_die_size || 12}`,
              rolls: cost.rolls, modifier: 0,
              damage_type: cost.grant.self_damage_type || "necrotic",
              total: cost.total, applied_total: cost.total,
            }],
            hp_before: cost.hpBefore, hp_after: cost.hpAfter,
            temporary_hp_before: cost.tempBefore, temporary_hp_after: cost.tempAfter,
            animation: "spell-overchannel",
            description: `${caster.state.template.name} suffers ${cost.total} ${cost.grant.self_damage_type || "necrotic"} damage from repeated use of ${cost.grant.source_name}.`,
          });
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser save-spell resolution failed", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_RESOLUTION = { resolve, resolveEffect, saveAction };
})();
