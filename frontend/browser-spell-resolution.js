(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function saveAction(choice) {
    const spell = choice.action;
    const extra = Math.max(0, choice.slotLevel - spell.level);
    return {
      id: spell.id, name: spell.name, saveAbility: spell.saveAbility, dc: spell.dc,
      range: spell.range + (spell.areaRadius || 0),
      damageDiceCount: spell.damageDiceCount + extra * (spell.upcastDicePerLevel || 0),
      damageDiceSize: spell.damageDiceSize, damageBonus: spell.damageBonus || 0,
      damageType: spell.damageType, successDamage: spell.successDamage || "none",
      animation: spell.animation || "spell-save",
    };
  }

  function resolve(sequence, round, caster, setup, choice, turnKey) {
    const spell = choice.action;
    if (spell.actionCost === "reaction") throw new Error("Reaction spells require their trigger window.");
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
      const event = V().resolveAction(
        sequence++, round, caster, target, action, S().distance(caster, target),
        { spendAction: false, sharedDamageRolls },
      );
      events.push(event);
      if (sharedDamageRolls == null && event.damage_components?.length) {
        sharedDamageRolls = [...event.damage_components[0].rolls];
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SPELL_RESOLUTION = { resolve, saveAction };
})();
