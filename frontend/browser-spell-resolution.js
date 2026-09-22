(() => {
  "use strict";

  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function saveAction(choice) {
    const spell = choice.action;
    if (choice.slotLevel !== spell.level) throw new Error("Spell upcasting is not certified; use the spell's printed slot level.");
    return {
      id: spell.id, name: spell.name, saveAbility: spell.saveAbility, dc: spell.dc,
      range: spell.range + (spell.areaRadius || 0),
      damageDiceCount: spell.damageDiceCount,
      damageDiceSize: spell.damageDiceSize, damageBonus: spell.damageBonus || 0,
      damageType: spell.damageType, successDamage: spell.successDamage || "none",
      animation: spell.animation || "spell-save",
    };
  }

  function damageTempHp(sequence, round, caster, spell, events) {
    const rule = caster.state.template.damaging_action_temporary_hp_rider;
    if (!rule || !(rule.action_ids || []).includes(spell.id)) return null;
    const dealt = events.some((event) => (event.damage_components || []).some((part) =>
      (part.applied_total ?? part.appliedTotal ?? part.total ?? 0) > 0));
    if (!dealt) return null;
    const score = caster.state.template.ability_scores?.[rule.ability];
    if (!Number.isInteger(score)) throw new Error("Ability-scaled Temporary HP requires ability scores.");
    const amount = Math.max(0, Math.floor((score - 10) / 2) * (rule.multiplier || 1));
    const before = caster.state.temporary_hp || 0;
    const after = S().grantTemporaryHp(caster.state, amount);
    if (after <= before) return null;
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      target_id: caster.combatant_id, target_name: caster.state.template.name,
      temporary_hp_before: before, temporary_hp_after: after,
      feature_id: rule.source_id, animation: "temporary-hp",
      description: caster.state.template.name + " gains " + (after - before)
        + " Temporary HP from " + rule.source_id.replaceAll("-", " ") + ".",
    };
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
      const ward = spell.areaRadius ? null : (window.IRON_PIT_BROWSER_TARGETING_WARDS?.check(caster, target) || null);
      if (ward && !ward.succeeded) {
        events.push(window.IRON_PIT_BROWSER_TARGETING_WARDS.blocked(sequence++, round, caster, target, spell.name, ward));
        continue;
      }
      const event = V().resolveAction(
        sequence, round, caster, target, action, S().distance(caster, target),
        { spendAction: false, sharedDamageRolls },
      );
      sequence += 1;
      if (ward) window.IRON_PIT_BROWSER_TARGETING_WARDS.annotate(event, ward, caster.state.template.name);
      const chain = DR() ? DR().chain(sequence, round, caster, event, setup, turnKey)
        : { events: [event], sequence };
      events.push(...chain.events); sequence = chain.sequence;
      if (sharedDamageRolls == null && event.damage_components?.length) {
        sharedDamageRolls = [...event.damage_components[0].rolls];
      }
    }
    const rider = damageTempHp(sequence, round, caster, spell, events);
    if (rider) { events.push(rider); sequence += 1; }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SPELL_RESOLUTION = { resolve, saveAction };
})();
