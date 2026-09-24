(() => {
  "use strict";

  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const DB = () => window.IRON_PIT_BROWSER_SPELL_DAMAGE_BONUS;

  function saveAction(choice, casterState) {
    const spell = choice.action;
    if (choice.slotLevel < spell.level) throw new Error("Spell cast level cannot be below the spell's printed level.");
    if (spell.level === 0 && choice.slotLevel !== 0) throw new Error("Cantrips cannot expend spell slots.");
    const upcastLevels = choice.slotLevel - spell.level;
    if ((spell.damageComponents || []).length && upcastLevels && (spell.upcastDicePerLevel || 0)) {
      throw new Error("Split-component spell upcasting requires explicit component scaling data.");
    }
    let damageBonus = spell.damageBonus || 0;
    let damageComponents = (spell.damageComponents || []).map((component) => ({ ...component }));
    const usedSources = new Set();
    if (damageComponents.length) {
      damageComponents = damageComponents.map((component) => {
        const result = DB()?.matches(casterState, spell.id, component.damageType, [...usedSources])
          || { total: 0, sources: [] };
        result.sources.forEach((source) => usedSources.add(source.sourceId));
        return { ...component, damageBonus: (component.damageBonus || 0) + result.total };
      });
    } else if (spell.damageType) {
      damageBonus += DB()?.matches(casterState, spell.id, spell.damageType).total || 0;
    }
    return {
      id: spell.id, name: spell.name, saveAbility: spell.saveAbility, dc: spell.dc,
      range: spell.range + (spell.areaRadius || 0),
      damageDiceCount: (spell.damageDiceCount || 0) + upcastLevels * (spell.upcastDicePerLevel || 0),
      damageDiceSize: spell.damageDiceSize, damageBonus,
      damageType: spell.damageType, damageComponents,
      successDamage: spell.successDamage || "none",
      magicalEffect: true, spellEffect: true, animation: spell.animation || "spell-save",
    };
  }

  function resolve(sequence, round, caster, setup, choice, turnKey) {
    const spell = choice.action;
    if (spell.actionCost === "reaction") throw new Error("Reaction spells require their trigger window.");
    if (choice.slotLevel < spell.level) throw new Error("Spell cast level cannot be below the spell's printed level.");
    if (spell.level === 0 && choice.slotLevel !== 0) throw new Error("Cantrips cannot expend spell slots.");
    if (!E().available(caster.state, spell.actionCost)) throw new Error(`${spell.actionCost} is unavailable for ${spell.name}.`);

    let remaining = null;
    const freeGrant = choice.slotLevel > 0 ? C().availableFreeSpellCast(caster.state, spell.id) : null;
    if (freeGrant) {
      remaining = C().consumeFreeSpellCast(caster.state, freeGrant);
    } else if (choice.slotLevel > 0) {
      const resourceId = `spell-slot-${choice.slotLevel}`;
      if (!(caster.state.resources?.[resourceId] > 0)) throw new Error(`No level ${choice.slotLevel} spell slot remains.`);
      C().markSlotSpellCast(caster.state, turnKey);
      caster.state.resources[resourceId] -= 1;
      remaining = caster.state.resources[resourceId];
    }
    E().spend(caster.state, spell.actionCost);
    window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.removeOwnerAttackEnding(caster.state);

    const placement = choice.placement;
    const detail = placement
      ? ` Area covers ${placement.enemyIds.length} enemies and ${placement.friendlyIds.length} unprotected allies.`
      : "";
    const slotText = choice.slotLevel === 0 ? "cantrip"
      : freeGrant ? `${freeGrant.source_name} without expending a spell slot`
        : `level ${choice.slotLevel} slot`;
    const events = [{
      sequence: sequence++, round_number: round, event_type: "feature",
      actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      feature_id: spell.id, resource_remaining: remaining, animation: spell.animation || "spell-save",
      description: `${caster.state.template.name} casts ${spell.name} using a ${slotText}.${detail}`,
    }];

    const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    const action = saveAction(choice, caster.state);
    let sharedDamageRolls = null;
    let sharedDamageComponentRolls = null;
    for (const targetId of choice.targetIds) {
      const target = members.get(targetId);
      const ward = spell.areaRadius ? null : (window.IRON_PIT_BROWSER_TARGETING_WARDS?.check(caster, target) || null);
      if (ward && !ward.succeeded) {
        events.push(window.IRON_PIT_BROWSER_TARGETING_WARDS.blocked(sequence++, round, caster, target, spell.name, ward));
        continue;
      }
      const event = V().resolveAction(
        sequence, round, caster, target, action, S().distance(caster, target),
        { spendAction: false, sharedDamageRolls, sharedDamageComponentRolls },
      );
      sequence += 1;
      if (ward) window.IRON_PIT_BROWSER_TARGETING_WARDS.annotate(event, ward, caster.state.template.name);
      const chain = DR() ? DR().chain(sequence, round, caster, event, setup, turnKey)
        : { events: [event], sequence };
      events.push(...chain.events); sequence = chain.sequence;
      if (event.damage_components?.length) {
        if (action.damageComponents?.length && sharedDamageComponentRolls == null) {
          sharedDamageComponentRolls = event.damage_components.map((component) => [...component.rolls]);
        } else if (!action.damageComponents?.length && sharedDamageRolls == null) {
          sharedDamageRolls = [...event.damage_components[0].rolls];
        }
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SPELL_RESOLUTION = { resolve, saveAction };
})();
