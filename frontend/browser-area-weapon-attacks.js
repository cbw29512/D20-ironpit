(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const AT = () => window.IRON_PIT_BROWSER_ATTACK;
  const D = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  const allMembers = (setup) => [...setup.heroes, ...setup.monsters];
  const attackById = (member, id) => (member.state.template.attacks || [])
    .find((attack) => attack.id === id) || null;

  function legalTargetIds(member, setup, attack, placement) {
    const byId = new Map(allMembers(setup).map((target) => [target.combatant_id, target]));
    const maximum = attack.long || attack.normal || attack.reach || 5;
    return placement.targetIds.filter((id) => {
      const target = byId.get(id);
      return target && S().distance(member, target) <= maximum;
    });
  }

  function choose(member, setup, requireAction = true) {
    try {
      if (requireAction && !E().available(member.state, "action")) return null;
      const normalCount = member.state.template.attack_action?.slots?.length || 1;
      const choices = [];
      for (const action of member.state.template.area_weapon_attack_actions || []) {
        const attackId = action.attackId || action.attack_id;
        const attack = attackById(member, attackId);
        if (!attack) throw new Error("Unknown area-weapon attack id " + attackId + ".");
        const rangeFt = action.range ?? action.range_ft;
        for (const placement of A().legalPlacements(member, setup, action.area, rangeFt)) {
          const targetIds = legalTargetIds(member, setup, attack, placement);
          if (targetIds.length <= normalCount) continue;
          choices.push({ action, attack, placement: { ...placement, targetIds } });
        }
      }
      return choices.sort((left, right) =>
        right.placement.targetIds.length - left.placement.targetIds.length)[0] || null;
    } catch (error) {
      console.error("Failed browser area weapon attack selection", { member: member.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, choice) {
    try {
      if (!E().available(member.state, "action")) {
        throw new Error("Area weapon attack requires an available Action.");
      }
      E().spend(member.state, "action");
      const byId = new Map(allMembers(setup).map((target) => [target.combatant_id, target]));
      const events = [];
      const turnKey = String(round) + ":" + member.combatant_id;
      for (const id of choice.placement.targetIds) {
        if (member.state.turn_terminated || member.state.is_dead || Q()?.incapacitated?.(member.state)) break;
        const target = byId.get(id);
        if (!target || target.state.is_dead || !target.state.is_alive) continue;
        const event = AT().resolveAttack(
          sequence, round, member, target, choice.attack, S().distance(member, target),
          { spendAction: false, setup, featureId: choice.action.id, turnKey },
        );
        sequence += 1;
        const chain = D()?.chain(sequence, round, member, event, setup, turnKey)
          || { events: [event], sequence };
        events.push(...chain.events);
        sequence = chain.sequence;
      }
      return { events, sequence };
    } catch (error) {
      console.error("Failed browser area weapon attack resolution", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_AREA_WEAPON_ATTACKS = { choose, resolve };
})();