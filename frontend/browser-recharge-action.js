(() => {
  "use strict";

  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const U = () => window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_CHARGE;
  const A = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const T = () => window.IRON_PIT_BROWSER_SAVE_TARGETS;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;

  function rechargeDefinitions(member) {
    return member.state.template.resourceDefinitions || {};
  }

  function usableRecharge(member, action) {
    const definition = rechargeDefinitions(member)[action.resourceId];
    return Boolean(action.resourceId && definition?.recharge
      && RES().available(member.state, action.resourceId, action.resourceCost || 1));
  }

  function rechargeSaveChoice(member, setup) {
    try {
      for (const target of F().targetOrder(member, setup)) {
        for (const action of member.state.template.saving_throw_actions || []) {
          if (action.area || !usableRecharge(member, action)) continue;
          const distance = F().saveDistance(member, target, action.range);
          if (V().legalAction(action, target, distance)) return { target, action, distance };
        }
      }
      return null;
    } catch (error) {
      console.error("Failed browser Recharge save choice", { member: member.combatant_id, error });
      throw error;
    }
  }

  function rechargeAreaSaveChoice(member, setup) {
    try {
      const members = new Map([...setup.heroes, ...setup.monsters].map((row) => [row.combatant_id, row]));
      const candidates = [];
      for (const [index, action] of (member.state.template.saving_throw_actions || []).entries()) {
        if (!action.area || !usableRecharge(member, action)) continue;
        for (const placement of A().legalPlacements(member, setup, action.area, action.range)) {
          const score = placement.targetIds.reduce((sum, id) => sum + O().saveAction(members.get(id), action), 0);
          candidates.push({ action, placement, score, index });
        }
      }
      candidates.sort((first, second) => second.score - first.score
        || second.placement.targetIds.length - first.placement.targetIds.length
        || first.index - second.index
        || first.placement.targetIds.join("|").localeCompare(second.placement.targetIds.join("|")));
      return candidates[0] || null;
    } catch (error) {
      console.error("Failed browser Recharge area-save choice", { member: member.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, turnKey) {
    try {
      const save = rechargeSaveChoice(member, setup);
      const areaSave = rechargeAreaSaveChoice(member, setup);
      const attack = F().chooseRechargeAttack(member, setup);
      const legal = [save && "save", areaSave && "area-save", attack && "attack"].filter(Boolean);
      if (legal.length > 1) throw new Error("Multiple legal Recharge action families require source-priority metadata.");
      if (save) {
        const event = V().resolveAction(sequence, round, member, save.target, save.action, save.distance);
        return { events: [event], sequence: sequence + 1, handled: true };
      }
      if (areaSave) {
        const result = T().resolveArea(sequence, round, member, setup, areaSave.action, { placement: areaSave.placement });
        return { events: result.events, sequence: result.sequence, handled: true };
      }
      if (attack) {
        const pack = S().packTactics(member, attack.target, setup);
        const opener = C()?.openingFeature?.(round, member, setup) || null;
        const result = U().resolve(sequence, round, member, attack.target, attack.attack, attack.distance, setup, turnKey, {
          advantage: pack ? 1 : 0,
          featureId: opener || (pack ? "pack-tactics" : null),
        });
        return { events: result.events, sequence: result.sequence, handled: true };
      }
      return { events: [], sequence, handled: false };
    } catch (error) {
      console.error("Failed browser Recharge action resolution", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RECHARGE_ACTION = {
    rechargeAreaSaveChoice, rechargeSaveChoice, resolve,
  };
})();
