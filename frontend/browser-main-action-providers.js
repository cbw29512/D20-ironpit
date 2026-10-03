(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION, DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const C = () => S().CATEGORIES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const L = () => window.IRON_PIT_BROWSER_SPELL_OFFENSE;
  const IP = () => window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014;
  const M = () => window.IRON_PIT_BROWSER_MULTIATTACK;
  const AS = () => window.IRON_PIT_BROWSER_AREA_SAVES;
  const AW = () => window.IRON_PIT_BROWSER_AREA_WEAPON_ATTACKS;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const HK = () => window.IRON_PIT_BROWSER_HP_THRESHOLD_INSTANT_DEATH;
  const HT = () => window.IRON_PIT_BROWSER_HP_THRESHOLD_CONDITION;
  const U = () => window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION;
  const DG = () => window.IRON_PIT_BROWSER_DODGE;
  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const CH = () => window.IRON_PIT_BROWSER_CHARGE;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;

  const BOTH = Object.freeze(["2014", "2024"]);
  function saveChoice(member, setup) {
    if (!E().available(member.state, "action")) return null;
    const orderedTargets = F().targetOrder(member, setup);
    for (const action of member.state.template.saving_throw_actions || []) {
      if ((action.actionCost || "action") !== "action" || (action.maxTargets || 1) <= 1) continue;
      if (action.resourceId && !R().available(member.state, action.resourceId, action.resourceCost || 1)) continue;
      const targets = orderedTargets.filter((target) => {
        const distance = F().saveDistance(member, target, action.range);
        return V().legalAction(action, target, distance)
          && (!action.requiresTargetSight || window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(member.state, target.state));
      }).slice(0, action.maxTargets);
      if (targets.length) return { targets, action };
    }
    for (const target of orderedTargets) {
      for (const action of member.state.template.saving_throw_actions || []) {
        if ((action.actionCost || "action") !== "action" || (action.maxTargets || 1) > 1) continue;
        if (action.resourceId && !R().available(member.state, action.resourceId, action.resourceCost || 1)) continue;
        const distance = F().saveDistance(member, target, action.range);
        if (V().legalAction(action, target, distance)) return { target, action, distance };
      }
    }
    return null;
  }

  function resolveMultiSave(sequence, round, member, setup, action, targets) {
    if (!targets.length || targets.length > (action.maxTargets || 1)) {
      throw new Error("Multi-target save selection violates its declared target cap.");
    }
    if (!E().available(member.state, action.actionCost || "action")) throw new Error(`${action.name} Action is unavailable.`);
    if (action.resourceId && !R().available(member.state, action.resourceId, action.resourceCost || 1)) {
      throw new Error(`${action.name} resource is unavailable.`);
    }
    for (const target of targets) {
      const distance = F().saveDistance(member, target, action.range);
      if (!V().legalAction(action, target, distance)
        || (action.requiresTargetSight && !window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(member.state, target.state))) {
        throw new Error(`${action.name} has an illegal selected target.`);
      }
    }
    const remaining = action.resourceId ? R().spend(member.state, action.resourceId, action.resourceCost || 1) : null;
    E().spend(member.state, action.actionCost || "action");
    const events = [];
    for (const target of targets) {
      const distance = F().saveDistance(member, target, action.range);
      const event = V().resolveAction(sequence, round, member, target, action, distance, {
        setup, spendAction: false, checkResource: false, spendResource: false, resourceRemaining: remaining,
      });
      if (DR()) {
        const chain = DR().chain(sequence + 1, round, member, event, setup);
        events.push(...chain.events); sequence = chain.sequence;
      } else {
        events.push(event); sequence += 1;
      }
    }
    return { events, sequence };
  }

  const memberById = (setup, id) => [...setup.heroes, ...setup.monsters]
    .find((member) => member.combatant_id === id) || null;
  const actionById = (member, id) => (member.state.template.saving_throw_actions || [])
    .find((action) => action.id === id) || null;
  const register = (descriptor) => S().registerProvider(descriptor);

  function install() {
    const selection = S();
    if (!selection) throw new Error("Main Action provider installation requires browser-main-action-selection.js.");

    register({
      id: "spell-offense", category: C().SPELL_OFFENSE, rulesets: BOTH,
      discover: ({ member, setup, turnKey }) => {
        const selected = L().choose(member, setup, turnKey);
        return selected ? { payload: { selected } } : null;
      },
      resolve: ({ sequence, round, member, setup, turnKey }, candidate) =>
        L().resolveChoice(sequence, round, member, setup, turnKey, candidate.payload.selected),
    });

    register({
      id: "intimidating-presence-2014", category: C().INTIMIDATING_PRESENCE_2014, rulesets: ["2014"],
      discover: ({ member, setup }) => {
        if (!(member.state.template.intimidating_presence_2014_dc > 0)) return null;
        const runtime = IP();
        if (!runtime) throw new Error("Intimidating Presence runtime is not loaded.");
        const target = F().targetOrder(member, setup)[0] || null;
        return target && runtime.canUse(member, target) ? { payload: { targetId: target.combatant_id } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const runtime = IP();
        if (!runtime) throw new Error("Intimidating Presence runtime is not loaded.");
        const target = memberById(setup, candidate.payload.targetId);
        if (!target) throw new Error("Intimidating Presence candidate target is unavailable.");
        const event = runtime.resolve(sequence, round, member, target);
        if (!event) throw new Error("Intimidating Presence candidate became illegal before resolution.");
        return { events: [event], sequence: sequence + 1 };
      },
    });

    register({
      id: "area-weapon-attack", category: C().AREA_WEAPON_ATTACK, rulesets: BOTH,
      discover: ({ member, setup, opportunityProfile }) => {
        const runtime = AW();
        if (!runtime) {
          if (member.state.template.area_weapon_attack_actions?.length) {
            throw new Error("Area weapon attack runtime is not loaded.");
          }
          return null;
        }
        const selected = runtime.choose(member, setup, opportunityProfile !== "actionSurgeAttack");
        return selected ? { payload: { selected } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) =>
        AW().resolve(sequence, round, member, setup, candidate.payload.selected),
    });

    register({
      id: "attack-action", category: C().ATTACK_ACTION, rulesets: BOTH,
      discover: ({ member, setup, opportunityProfile }) => {
        if (!member.state.template.attack_action) return null;
        const runtime = M();
        if (!runtime) throw new Error("Attack/Multiattack runtime is not loaded.");
        const legal = opportunityProfile === "actionSurgeAttack" ? runtime.legalChoiceAvailable(member, setup) : runtime.available(member, setup);
        return legal ? { payload: {} } : null;
      },
      resolve: ({ sequence, round, member, setup }) => {
        const runtime = M();
        if (!runtime) throw new Error("Attack/Multiattack runtime is not loaded.");
        return runtime.resolveAttackAction(sequence, round, member, setup);
      },
    });

    register({
      id: "area-save", category: C().AREA_SAVE, rulesets: BOTH,
      discover: ({ member, setup }) => {
        if (!E().available(member.state, "action")) return null;
        const selected = AS()?.choose(member, setup, "action") || null;
        return selected ? { payload: { selected } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const result = AS().resolve(sequence, round, member, setup, candidate.payload.selected);
        if (!result) throw new Error("Area-save candidate became illegal before resolution.");
        return { events: result.events, sequence: result.sequence };
      },
    });

    register({
      id: "save-action", category: C().SAVE_ACTION, rulesets: BOTH,
      discover: ({ member, setup }) => {
        const selected = saveChoice(member, setup);
        if (!selected) return null;
        if (selected.targets) return { payload: {
          targetIds: selected.targets.map((target) => target.combatant_id), actionId: selected.action.id,
        } };
        return { payload: {
          targetId: selected.target.combatant_id, actionId: selected.action.id, distance: selected.distance,
        } };
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const action = actionById(member, candidate.payload.actionId);
        if (!action) throw new Error("Save-action candidate action is unavailable.");
        if (Array.isArray(candidate.payload.targetIds)) {
          const targets = candidate.payload.targetIds.map((id) => memberById(setup, id));
          if (targets.some((target) => !target)) throw new Error("Multi-save candidate target is unavailable.");
          return resolveMultiSave(sequence, round, member, setup, action, targets);
        }
        const target = memberById(setup, candidate.payload.targetId);
        if (!target) throw new Error("Save-action candidate target is unavailable.");
        const event = V().resolveAction(sequence, round, member, target, action, candidate.payload.distance, { setup });
        const next = sequence + 1;
        return DR() ? DR().chain(next, round, member, event, setup) : { events: [event], sequence: next };
      },
    });

    HK()?.installProvider();
    HT()?.installProvider();

    register({
      id: "standard-attack", category: C().STANDARD_ATTACK, rulesets: BOTH,
      discover: ({ member, setup, opportunityProfile }) => {
        if (opportunityProfile !== "actionSurgeAttack" && !E().available(member.state, "action")) return null;
        const choice = F().chooseStandardAttack(member, setup);
        return choice ? { payload: { targetId: choice.target.combatant_id, attackId: choice.attack.id, distance: choice.distance } } : null;
      },
      resolve: ({ sequence, round, member, setup, turnKey, opportunityProfile }, candidate) => {
        const target = memberById(setup, candidate.payload.targetId);
        const attack = (member.state.template.attacks || []).find((item) => item.id === candidate.payload.attackId);
        if (!target || !attack) throw new Error("Standard-attack candidate target/attack is unavailable.");
        const pack = ST().packTactics(member, target, setup);
        const surge = opportunityProfile === "actionSurgeAttack";
        const opener = surge ? null : (CH()?.openingFeature?.(round, member, setup) || null);
        return U().resolve(sequence, round, member, target, attack, candidate.payload.distance, setup, turnKey, {
          advantage: pack ? 1 : 0, featureId: surge ? "action-surge" : (opener || (pack ? "pack-tactics" : null)),
        });
      },
    });

    register({
      id: "dodge", category: C().DODGE, rulesets: BOTH,
      discover: ({ member }) => E().available(member.state, "action") ? { payload: {} } : null,
      resolve: ({ sequence, round, member }) => ({
        events: [DG().take(sequence, round, member)], sequence: sequence + 1,
      }),
    });
  }

  install();
  window.IRON_PIT_BROWSER_MAIN_ACTION_PROVIDERS = { install, saveChoice };
})();
