(() => {
  "use strict";

  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const U = () => window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_CHARGE;

  function rechargeSaveChoice(member, setup) {
    try {
      const definitions = member.state.template.resourceDefinitions || {};
      for (const target of F().targetOrder(member, setup)) {
        for (const action of member.state.template.saving_throw_actions || []) {
          if (!action.resourceId || !definitions[action.resourceId]?.recharge) continue;
          if (!RES().available(member.state, action.resourceId, action.resourceCost || 1)) continue;
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

  function resolve(sequence, round, member, setup, turnKey) {
    try {
      const save = rechargeSaveChoice(member, setup);
      const attack = F().chooseRechargeAttack(member, setup);
      if (save && attack) throw new Error("Multiple legal Recharge action families require source-priority metadata.");
      if (save) {
        const event = V().resolveAction(sequence, round, member, save.target, save.action, save.distance);
        return { events: [event], sequence: sequence + 1, handled: true };
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

  window.IRON_PIT_BROWSER_RECHARGE_ACTION = { rechargeSaveChoice, resolve };
})();
