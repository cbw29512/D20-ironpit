(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_REFLECTION;
  const dimension = (area, camel, snake) => area?.[camel] ?? area?.[snake] ?? 0;
  const creatureType = (target) => (target.state.template.creature_type || "").toLowerCase();
  const rule = (spell, field) => spell[field] || window.IRON_PIT_BROWSER_SPELL_TARGET_RULES?.[spell.id]?.[field] || [];
  const spellAffects = (spell, target) => !rule(spell, "excludedCreatureTypes").includes(creatureType(target)) && C().affectsTarget(target.state, spell.level);

  function effectReach(spell) {
    if (!spell.area) return spell.range + (spell.areaRadius || 0);
    const extent = dimension(spell.area, "radiusFt", "radius_ft") || dimension(spell.area, "lengthFt", "length_ft");
    return spell.area.origin === "point" ? spell.range + extent : extent;
  }

  function saveAction(choice) {
    const spell = choice.action;
    if (choice.slotLevel !== spell.level) throw new Error("Spell upcasting is not certified; use the spell's printed slot level.");
    return {
      id: spell.id, name: spell.name, saveAbility: spell.saveAbility, dc: spell.dc,
      range: effectReach(spell), damageDiceCount: spell.damageDiceCount,
      damageDiceSize: spell.damageDiceSize, damageBonus: spell.damageBonus || 0,
      damageType: spell.damageType, successDamage: spell.successDamage || "none",
      failurePushFt: spell.failurePushFt || 0,
      magicalEffect: true, animation: spell.animation || "spell-save",
    };
  }

  function targetSave(spell, target, action) {
    const disadvantage = rule(spell, "saveDisadvantageCreatureTypes").includes(creatureType(target)) ? 1 : 0;
    return disadvantage ? V().resolveSavingThrow(target.state, action.saveAbility, action.dc,
      { magicalEffect: true, disadvantageSources: disadvantage }) : null;
  }

  function targetDamageRolls(spell, target) {
    if (!rule(spell, "maximizeDamageCreatureTypes").includes(creatureType(target))) return null;
    return Array(spell.damageDiceCount || 0).fill(spell.damageDiceSize);
  }

  function resolve(sequence, round, caster, setup, choice, turnKey) {
    const spell = choice.action;
    if (spell.actionCost === "reaction") throw new Error("Reaction spells require their trigger window.");
    if (choice.slotLevel !== spell.level) throw new Error("Spell upcasting is not certified; use the spell's printed slot level.");
    if (!E().available(caster.state, spell.actionCost)) throw new Error(`${spell.actionCost} is unavailable for ${spell.name}.`);

    let remaining = null;
    if (choice.slotLevel > 0) {
      const resourceId = `spell-slot-${choice.slotLevel}`;
      if (!(caster.state.resources?.[resourceId] > 0)) throw new Error(`No level ${choice.slotLevel} spell slot remains.`);
      C().markSlotSpellCast(caster.state, turnKey); caster.state.resources[resourceId] -= 1;
      remaining = caster.state.resources[resourceId];
    }
    E().spend(caster.state, spell.actionCost);

    const placement = choice.placement;
    const detail = placement ? ` Area covers ${placement.enemyIds.length} enemies and ${placement.friendlyIds.length} unprotected allies.` : "";
    const slotText = choice.slotLevel === 0 ? "cantrip" : `level ${choice.slotLevel} slot`;
    const events = [{
      sequence: sequence++, round_number: round, event_type: "feature",
      actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      feature_id: spell.id, resource_remaining: remaining, animation: spell.animation || "spell-save",
      description: `${caster.state.template.name} casts ${spell.name} using a ${slotText}.${detail}`,
    }];

    const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    const action = saveAction(choice), reflectable = !spell.area && !spell.areaRadius && choice.targetIds.length === 1;
    let sharedDamageRolls = null;
    for (const targetId of choice.targetIds) {
      let target = members.get(targetId), precomputedSave = null, reflectedFrom = null;
      if (!spellAffects(spell, target)) continue;
      if (reflectable && target.state.template.spell_reflection_reaction) {
        const disadvantage = rule(spell, "saveDisadvantageCreatureTypes").includes(creatureType(target)) ? 1 : 0;
        precomputedSave = V().resolveSavingThrow(target.state, action.saveAbility, action.dc,
          { magicalEffect: true, disadvantageSources: disadvantage });
        if (precomputedSave.succeeded) {
          const reflected = SR()?.target(target, caster, setup);
          if (reflected) { SR().spend(target); reflectedFrom = target; target = reflected; precomputedSave = null; }
        }
      }
      if (!spellAffects(spell, target)) continue;
      if (!precomputedSave) precomputedSave = targetSave(spell, target, action);
      const maximized = targetDamageRolls(spell, target), damageRolls = maximized || sharedDamageRolls;
      const event = V().resolveAction(
        sequence++, round, caster, target, action,
        placement || reflectedFrom ? 0 : S().distance(caster, target),
        { spendAction: false, sharedDamageRolls: damageRolls, precomputedSave, setup },
      );
      if (reflectedFrom) event.description = `${reflectedFrom.state.template.name} uses Spell Reflection; ${spell.name} targets ${target.state.template.name} instead. ${event.description}`;
      events.push(event);
      if (!maximized && sharedDamageRolls == null && event.damage_components?.length) sharedDamageRolls = [...event.damage_components[0].rolls];
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SPELL_RESOLUTION = { resolve, saveAction };
})();
