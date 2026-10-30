(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const AS = () => window.IRON_PIT_BROWSER_AREA_SAVES;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const U = () => window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION;
  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const CH = () => window.IRON_PIT_BROWSER_CHARGE;
  const MS = () => window.IRON_PIT_BROWSER_MULTI_SAVE_PROVIDER;
  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;

  function rechargeIds(member) {
    try {
      return new Set((member.state.template.recharge_rules || []).map((rule) => rule.resourceId));
    } catch (error) {
      console.error("Failed browser Recharge resource discovery", { member: member.combatant_id, error });
      throw error;
    }
  }

  function isRecharge(member, action) {
    try {
      return Boolean(action?.resourceId && rechargeIds(member).has(action.resourceId));
    } catch (error) {
      console.error("Failed browser Recharge action classification", { member: member.combatant_id, action: action?.id, error });
      throw error;
    }
  }

  function printedSave(action, target = null) {
    try {
      const printed = (action.damageDiceCount || 0) * ((action.damageDiceSize || 6) + 1) / 2
        + (action.damageBonus || 0);
      if (!action.failureSetsZeroHp || target == null) return printed;
      const hp = target.state?.current_hp;
      if (!Number.isFinite(hp) || hp < 0) {
        throw new Error("Zero-HP action ranking requires valid current target HP.");
      }
      return Math.max(printed, hp);
    } catch (error) {
      console.error("Failed browser zero-HP save impact ranking", { action: action?.id, error });
      throw error;
    }
  }

  function saveChoice(member, setup, predicate = null) {
    try {
      if (!E().available(member.state, "action")) return null;
      const actions = member.state.template.saving_throw_actions || [];
      if (predicate && actions.some((action) =>
        predicate(action) && (action.maxTargets || 1) > 1 && !action.area)) {
        throw new Error("Recharge multi-target save priority requires shared filtered multi-save selection.");
      }
      if (!predicate && actions.some((action) => (action.maxTargets || 1) > 1)) {
        const selected = MS()?.choose(member, setup);
        if (selected) return selected;
      }
      for (const target of F().targetOrder(member, setup)) {
        for (const action of actions) {
          if (predicate && !predicate(action)) continue;
          if ((action.actionCost || "action") !== "action" || action.area
            || (action.maxTargets || 1) > 1) continue;
          if (action.resourceId
            && !R().available(member.state, action.resourceId, action.resourceCost || 1)) continue;
          const distance = F().saveDistance(member, target, action.range);
          if (V().legalAction(action, target, distance, member.combatant_id, member)) {
            return { target, action, distance };
          }
        }
      }
      return null;
    } catch (error) {
      console.error("Failed browser save-action choice", { member: member.combatant_id, error });
      throw error;
    }
  }

  function rechargeChoices(member, setup) {
    try {
      const predicate = (action) => isRecharge(member, action);
      const area = AS()?.choose(member, setup, "action", false, predicate) || null;
      const save = saveChoice(member, setup, predicate);
      const attackIds = (member.state.template.attacks || [])
        .filter((attack) => isRecharge(member, attack)).map((attack) => attack.id);
      const attack = attackIds.length ? F().chooseAttack(member, setup, attackIds) : null;
      return [area ? "area-save" : null, save ? "save-action" : null,
        attack ? "standard-attack" : null].filter(Boolean);
    } catch (error) {
      console.error("Failed browser Recharge choice discovery", { member: member.combatant_id, error });
      throw error;
    }
  }

  function priorityScore(member, setup, action) {
    try {
      if (!isRecharge(member, action)) return null;
      const families = rechargeChoices(member, setup);
      if (new Set(families).size > 1) {
        throw new Error("Multiple legal Recharge Action families require explicit source-priority policy.");
      }
      return Number.POSITIVE_INFINITY;
    } catch (error) {
      console.error("Failed browser Recharge priority scoring", { member: member.combatant_id, action: action?.id, error });
      throw error;
    }
  }

  function memberById(setup, id) {
    try {
      return [...setup.heroes, ...setup.monsters].find((member) => member.combatant_id === id) || null;
    } catch (error) {
      console.error("Failed browser Main Action member lookup", { id, error });
      throw error;
    }
  }

  function actionById(member, id) {
    try {
      return (member.state.template.saving_throw_actions || []).find((action) => action.id === id) || null;
    } catch (error) {
      console.error("Failed browser save Action lookup", { member: member.combatant_id, id, error });
      throw error;
    }
  }

  function install() {
    try {
      const register = (descriptor) => S().registerProvider(descriptor);
      const C = S().CATEGORIES;
      register({ id: "area-save", category: C.AREA_SAVE, rulesets: ["2014", "2024"],
        discover: ({ member, setup }) => {
          if (!E().available(member.state, "action")) return null;
          const selected = AS()?.choose(member, setup, "action") || null;
          if (!selected) return null;
          return { payload: { selected, delivery: "ability",
            expectedDamage: priorityScore(member, setup, selected.action)
              ?? printedSave(selected.action) * (selected.placement?.targetIds?.length || 1) } };
        },
        resolve: ({ sequence, round, member, setup }, candidate) => {
          const result = AS().resolve(sequence, round, member, setup, candidate.payload.selected);
          if (!result) throw new Error("Area-save candidate became illegal before resolution.");
          return { events: result.events, sequence: result.sequence };
        } });
      register({ id: "save-action", category: C.SAVE_ACTION, rulesets: ["2014", "2024"],
        discover: ({ member, setup }) => {
          const selected = saveChoice(member, setup);
          if (!selected) return null;
          const score = priorityScore(member, setup, selected.action);
          if (selected.targets) return { payload: { targetIds: selected.targets.map((target) => target.combatant_id),
            actionId: selected.action.id, delivery: "ability",
            expectedDamage: score ?? selected.targets.reduce((sum, target) => sum + printedSave(selected.action, target), 0) } };
          return { payload: { targetId: selected.target.combatant_id, actionId: selected.action.id,
            distance: selected.distance, delivery: "ability",
            expectedDamage: score ?? printedSave(selected.action, selected.target) } };
        },
        resolve: ({ sequence, round, member, setup }, candidate) => {
          const action = actionById(member, candidate.payload.actionId);
          if (!action) throw new Error("Save-action candidate action is unavailable.");
          if (Array.isArray(candidate.payload.targetIds)) {
            const targets = candidate.payload.targetIds.map((id) => memberById(setup, id));
            if (targets.some((target) => !target)) throw new Error("Multi-save candidate target is unavailable.");
            return MS().resolve(sequence, round, member, setup, action, targets);
          }
          const target = memberById(setup, candidate.payload.targetId);
          if (!target) throw new Error("Save-action candidate target is unavailable.");
          const event = V().resolveAction(sequence, round, member, target, action, candidate.payload.distance, { setup });
          return DR() ? DR().chain(sequence + 1, round, member, event, setup)
            : { events: [event], sequence: sequence + 1 };
        } });
      register({ id: "standard-attack", category: C.STANDARD_ATTACK, rulesets: ["2014", "2024"],
        discover: ({ member, setup, opportunityProfile }) => {
          if (opportunityProfile !== "actionSurgeAttack" && !E().available(member.state, "action")) return null;
          const recharge = (member.state.template.attacks || []).filter((attack) => isRecharge(member, attack));
          const choice = recharge.length
            ? F().chooseAttack(member, setup, recharge.map((attack) => attack.id))
            : F().chooseStandardAttack(member, setup);
          if (!choice) return null;
          return { payload: { targetId: choice.target.combatant_id, attackId: choice.attack.id,
            distance: choice.distance, delivery: choice.attack.kind,
            expectedDamage: priorityScore(member, setup, choice.attack) ?? F().weaponMeanDamage(choice.attack) } };
        },
        resolve: ({ sequence, round, member, setup, turnKey, opportunityProfile }, candidate) => {
          const target = memberById(setup, candidate.payload.targetId);
          const attack = (member.state.template.attacks || []).find((item) => item.id === candidate.payload.attackId);
          if (!target || !attack) throw new Error("Standard-attack candidate target/attack is unavailable.");
          const pack = ST().packTactics(member, target, setup);
          const surge = opportunityProfile === "actionSurgeAttack";
          return U().resolve(sequence, round, member, target, attack, candidate.payload.distance, setup, turnKey, {
            advantage: pack ? 1 : 0,
            featureId: surge ? "action-surge"
              : (CH()?.openingFeature?.(round, member, setup) || (pack ? "pack-tactics" : null)),
          });
        } });
    } catch (error) {
      console.error("Failed browser offensive Main Action provider installation", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MAIN_ACTION_OFFENSE_PROVIDERS = { install, printedSave, saveChoice };
})();
