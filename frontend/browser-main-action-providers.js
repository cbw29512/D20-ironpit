(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION, DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const C = () => S().CATEGORIES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const L = () => window.IRON_PIT_BROWSER_SPELL_OFFENSE;
  const IP = () => window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014;
  const DE = () => window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT;
  const M = () => window.IRON_PIT_BROWSER_MULTIATTACK;
  const AS = () => window.IRON_PIT_BROWSER_AREA_SAVES;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const U = () => window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION;
  const DG = () => window.IRON_PIT_BROWSER_DODGE;
  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const CH = () => window.IRON_PIT_BROWSER_CHARGE;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;
  const RF = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORMS;
  const RFC = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORM_COMPILER;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;

  const BOTH = Object.freeze(["2014", "2024"]);
  function saveChoice(member, setup) {
    if (!E().available(member.state, "action")) return null;
    for (const target of F().targetOrder(member, setup)) {
      for (const action of member.state.template.saving_throw_actions || []) {
        const distance = F().saveDistance(member, target, action.range);
        if (V().legalAction(action, target, distance)) return { target, action, distance };
      }
    }
    return null;
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
      id: "replacement-form-setup", category: C().REPLACEMENT_FORM_SETUP, rulesets: BOTH,
      discover: ({ member, setup, turnKey }) => {
        if (member.state.replacement_form || !E().available(member.state, "action")) return null;
        const action = (member.state.template.replacement_form_actions || [])[0];
        if (!action) return null;
        if (!RES()?.available(member.state, action.resourceId, action.resourceCost || 1)) return null;
        if (action.setupSpellId && member.state.concentration?.effect_id !== action.setupSpellId) {
          const choice = SP()?.chooseById(member, setup, turnKey, action.setupSpellId) || null;
          return choice ? { payload: { kind: "setup-spell", choice } } : null;
        }
        const registry = member.state.template.ruleset === "2014"
          ? window.IRON_PIT_BROWSER_MONSTERS_2014 : window.IRON_PIT_BROWSER_MONSTERS;
        const source = registry?.[action.formTemplateId];
        if (!source) throw new Error(`Replacement-form source ${action.formTemplateId} is unavailable.`);
        return { payload: { kind: "transform", actionId: action.id, formTemplateId: action.formTemplateId } };
      },
      resolve: ({ sequence, round, member, setup, turnKey }, candidate) => {
        if (candidate.payload.kind === "setup-spell") {
          if (!SR()) throw new Error("Replacement-form setup spell requires browser-spell-resolution.js.");
          return SR().resolve(sequence, round, member, setup, candidate.payload.choice, turnKey);
        }
        if (candidate.payload.kind !== "transform") throw new Error("Unknown replacement-form setup candidate.");
        const action = (member.state.template.replacement_form_actions || [])
          .find((item) => item.id === candidate.payload.actionId);
        if (!action) throw new Error("Replacement-form action is unavailable.");
        const registry = member.state.template.ruleset === "2014"
          ? window.IRON_PIT_BROWSER_MONSTERS_2014 : window.IRON_PIT_BROWSER_MONSTERS;
        const source = registry?.[candidate.payload.formTemplateId];
        if (!source) throw new Error("Replacement-form source became unavailable.");
        if (!RFC() || !RF()) throw new Error("Replacement-form compiler/runtime is not loaded.");
        const active = RFC().compile(member.state.template, source, Boolean(action.retainSpellcasting));
        const result = RF().enter(member.state, action, active);
        return {
          events: [{
            sequence, round_number: round, event_type: "feature",
            actor_id: member.combatant_id, actor_name: member.state.template.name,
            feature_id: action.id, resource_remaining: result.resource_remaining,
            animation: "transform",
            description: `${member.state.template.name} uses ${action.name} and enters the ${source.name} replacement form.`,
          }],
          sequence: sequence + 1,
        };
      },
    });

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
      id: "deferred-effect", category: C().DEFERRED_EFFECT, rulesets: BOTH,
      discover: ({ member, setup }) => {
        const runtime = DE();
        if (!runtime) {
          if (member.state.template.deferred_save_effect) throw new Error("Deferred-effect runtime is not loaded.");
          return null;
        }
        const target = runtime.candidate(member, setup);
        return target ? { payload: { targetId: target.combatant_id } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const runtime = DE();
        if (!runtime) throw new Error("Deferred-effect runtime is not loaded.");
        const event = runtime.resolve(sequence, round, member, setup, candidate.payload.targetId);
        if (!event) throw new Error("Deferred-effect candidate became illegal before resolution.");
        return { events: [event], sequence: sequence + 1 };
      },
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
        const selected = AS()?.choose(member, setup) || null;
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
        return selected ? { payload: {
          targetId: selected.target.combatant_id, actionId: selected.action.id, distance: selected.distance,
        } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const target = memberById(setup, candidate.payload.targetId);
        const action = actionById(member, candidate.payload.actionId);
        if (!target || !action) throw new Error("Save-action candidate target/action is unavailable.");
        const event = V().resolveAction(sequence, round, member, target, action, candidate.payload.distance, { setup });
        const next = sequence + 1;
        return DR() ? DR().chain(next, round, member, event, setup) : { events: [event], sequence: next };
      },
    });

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
