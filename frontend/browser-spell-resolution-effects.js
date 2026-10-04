(() => {
  "use strict";

  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const SM = () => window.IRON_PIT_BROWSER_SPELL_MODIFIERS;
  const H = () => window.IRON_PIT_BROWSER_SPELL_SAVE_DISADVANTAGE;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;

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
        failedSavePushFt: spell.failedSavePushFt || 0,
        failedSaveTimedEffect: spell.failedSaveTimedEffect || null,
        requiredTargetCreatureTypes: [...(spell.requiredTargetCreatureTypes || [])],
        excludedTargetCreatureTypes: [...(spell.excludedTargetCreatureTypes || [])],
        minimumRemainingHp: spell.minimumRemainingHp || 0,
        reduceHitPointMaximumOnFailedSave: Boolean(spell.reduceHitPointMaximumOnFailedSave),
        requiresTargetHearing: Boolean(spell.requiresTargetHearing),
        requiresTargetSight: Boolean(spell.requiresTargetSight),
        automaticFailureCreatureTypes: [...(spell.automaticFailureCreatureTypes || [])],
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
      const dcBonus = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS?.spellSaveDcBonus?.(caster.state) || 0;
      if (dcBonus) action.dc += dcBonus;
      const events = [];
      let sharedDamageRolls = null;
      if (choice.damageMaximizer) {
        sharedDamageRolls = spell.damageComponents?.length
          ? spell.damageComponents.map((component) =>
            C().maximizedRolls(component.diceCount || 0, component.diceSize || 6))
          : C().maximizedRolls(spell.damageDiceCount || 0, spell.damageDiceSize || 6);
      }
      let saveDisadvantage = H()?.choose(caster.state, turnKey) || null;

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
          modifierRemaining = H().spend(caster.state, saveDisadvantage, turnKey);
          saveDisadvantageSources = [saveDisadvantage.name];
          saveDisadvantage = null;
        }
        const fighting = setup && caster.side !== target.side && (
          caster.side === "heroes" ? setup.heroes : setup.monsters
        ).some((ally) => ally.state.is_alive && !ally.state.is_dead && ally.state.current_hp > 0);
        const saveAdvantageSources = (
          spell.saveAdvantageIfFighting && fighting
        ) ? ["fighting-the-target"] : [];
        const event = V().resolveAction(
          sequence, round, caster, target, action,
          placement ? 0 : S().distance(caster, target),
          {
            spendAction: false, sharedDamageRolls, spellEffect: true, setup,
            saveDisadvantageSources, saveAdvantageSources, resourceRemaining: modifierRemaining,
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

  window.IRON_PIT_BROWSER_SPELL_RESOLUTION_EFFECTS = { scaledSpell, saveAction, resolveEffect };
})();
