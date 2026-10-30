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

  function resourceRank(member, resourceId) {
    try {
      if (!resourceId) throw new Error("Recharge action is missing its resource id.");
      const ids = Object.keys(rechargeDefinitions(member));
      const index = ids.indexOf(resourceId);
      if (index < 0) throw new Error(`Recharge resource ${resourceId} is not declared on the combatant.`);
      return index;
    } catch (error) {
      console.error("Failed browser Recharge source-priority probe", { member: member.combatant_id, resourceId, error });
      throw error;
    }
  }

  function rechargeSaveChoice(member, setup) {
    try {
      for (const target of F().targetOrder(member, setup)) {
        for (const action of member.state.template.saving_throw_actions || []) {
          if (action.area || !usableRecharge(member, action)) continue;
          const distance = F().saveDistance(member, target, action.range);
          if (V().legalAction(action, target, distance, member)) return { target, action, distance };
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

  function choiceResourceId(kind, payload) {
    if (kind === "attack") return payload.attack.resourceId;
    if (kind === "save") return payload.action.resourceId;
    if (kind === "area-save") return payload.action.resourceId;
    throw new Error(`Unsupported Recharge action family: ${kind}`);
  }

  function resolve(sequence, round, member, setup, turnKey) {
    try {
      const save = rechargeSaveChoice(member, setup);
      const areaSave = rechargeAreaSaveChoice(member, setup);
      const attack = F().chooseRechargeAttack(member, setup);
      const legal = [
        save && { kind: "save", payload: save },
        areaSave && { kind: "area-save", payload: areaSave },
        attack && { kind: "attack", payload: attack },
      ].filter(Boolean);
      legal.sort((first, second) => resourceRank(member, choiceResourceId(first.kind, first.payload))
        - resourceRank(member, choiceResourceId(second.kind, second.payload)));
      const chosen = legal[0] || null;
      if (!chosen) return { events: [], sequence, handled: false };

      if (chosen.kind === "save") {
        const { target, action, distance } = chosen.payload;
        const event = V().resolveAction(sequence, round, member, target, action, distance);
        return { events: [event], sequence: sequence + 1, handled: true };
      }
      if (chosen.kind === "area-save") {
        const { action, placement } = chosen.payload;
        const result = T().resolveArea(sequence, round, member, setup, action, { placement });
        return { events: result.events, sequence: result.sequence, handled: true };
      }
      if (chosen.kind === "attack") {
        const { target, attack, distance } = chosen.payload;
        const pack = S().packTactics(member, target, setup);
        const opener = C()?.openingFeature?.(round, member, setup) || null;
        const result = U().resolve(sequence, round, member, target, attack, distance, setup, turnKey, {
          advantage: pack ? 1 : 0,
          featureId: opener || (pack ? "pack-tactics" : null),
        });
        return { events: result.events, sequence: result.sequence, handled: true };
      }
      throw new Error(`Unsupported Recharge action family: ${chosen.kind}`);
    } catch (error) {
      console.error("Failed browser Recharge action resolution", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RECHARGE_ACTION = {
    rechargeAreaSaveChoice, rechargeSaveChoice, resolve,
  };
})();
