(() => {
  "use strict";

  const H = () => window.IRON_PIT_BROWSER_HEALING;
  const C = () => window.IRON_PIT_BROWSER_CONDITION_REMOVAL;
  const X = () => window.IRON_PIT_BROWSER_EFFECT_REMOVAL;
  const K = () => window.IRON_PIT_BROWSER_CLERIC_CHANNEL;
  const P = () => window.IRON_PIT_BROWSER_PALADIN_2014;
  const B = () => window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const D = () => window.IRON_PIT_DICE;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function resolve(sequence, round, member, setup, turnKey) {
    const events = [];
    let healing = H()?.chooseAction(member, setup, turnKey);
    if (healing?.target.state.current_hp === 0) {
      if ((healing.action.maxTargets || 1) > 1) {
        const targets = H().groupTargets(member, setup, healing.action, turnKey);
        if (targets.some((target) => target.state.current_hp === 0)) {
          const result = H().resolveGroup(sequence, round, member, targets, healing.action, turnKey);
          events.push(...result.events); sequence = result.sequence;
        }
      } else {
        const before = healing.target.state.current_hp;
        events.push(H().resolve(sequence++, round, member, healing.target, healing.action, turnKey));
        const rider = H().selfRider(sequence, round, member, healing.action,
          healing.target.combatant_id !== member.combatant_id && healing.target.state.current_hp > before);
        if (rider) events.push(rider), sequence += 1;
      }
    }
    const removal = C()?.chooseAction(member, setup, turnKey);
    if (removal) {
      events.push(C().resolve(sequence++, round, member, removal.target, removal.action, removal.conditions, turnKey));
    }
    healing = H()?.chooseAction(member, setup, turnKey);
    if (healing) {
      if ((healing.action.maxTargets || 1) > 1) {
        const targets = H().groupTargets(member, setup, healing.action, turnKey);
        if (targets.length) {
          const result = H().resolveGroup(sequence, round, member, targets, healing.action, turnKey);
          events.push(...result.events); sequence = result.sequence;
        }
      } else {
        const before = healing.target.state.current_hp;
        events.push(H().resolve(sequence++, round, member, healing.target, healing.action, turnKey));
        const rider = H().selfRider(sequence, round, member, healing.action,
          healing.target.combatant_id !== member.combatant_id && healing.target.state.current_hp > before);
        if (rider) events.push(rider), sequence += 1;
      }
    }
    const effectRemoval = X()?.choose(member, setup, turnKey);
    if (effectRemoval) events.push(X().resolve(sequence++, round, member, setup, effectRemoval.action, effectRemoval.effect, turnKey));
    const cleric = member.state.template.class_id === "cleric" || member.state.template.archetype === "Cleric";
    const channel = cleric ? K()?.resolve(sequence, round, member, setup) : null;
    if (channel) { events.push(...channel.events); sequence = channel.sequence; }
    const paladin = P()?.resolveChannel(sequence, round, member, setup);
    if (paladin) { events.push(...paladin.events); sequence = paladin.sequence; }
    const selfBuff = B()?.choose(member);
    if (selfBuff) events.push(B().resolve(sequence++, round, member, selfBuff));
    return { events, sequence };
  }

  function secondWind(sequence, round, member) {
    const state = member.state, uses = state.resources["second-wind"] || 0;
    if (!uses || !E().available(state, "bonus_action") || state.current_hp <= 0 || state.current_hp > Math.floor(state.template.max_hp / 2)) return null;
    const die = D().roll(10), total = die + state.template.level, before = state.current_hp;
    state.current_hp = Math.min(state.template.max_hp, state.current_hp + total);
    state.resources["second-wind"] -= 1; E().spend(state, "bonus_action");
    return { sequence, round_number: round, event_type: "healing", actor_id: member.combatant_id, actor_name: state.template.name,
      target_id: member.combatant_id, target_name: state.template.name, hp_before: before, hp_after: state.current_hp,
      healing_roll: { notation: `1d10+${state.template.level}`, rolls: [die], modifier: state.template.level, total },
      feature_id: "second-wind", resource_remaining: state.resources["second-wind"], animation: "second-wind",
      description: `${state.template.name} uses Second Wind and regains ${state.current_hp - before} HP.` };
  }

  function adrenaline(sequence, round, member) {
    const state = member.state, pb = 2 + Math.floor((state.template.level - 1) / 4);
    if (!state.template.traits?.includes("adrenaline-rush") || !E().available(state, "bonus_action")
        || !(state.resources["adrenaline-rush"] > 0) || state.temporary_hp >= pb) return null;
    state.resources["adrenaline-rush"] -= 1; E().spend(state, "bonus_action");
    S().grantTemporaryHp(state, pb);
    return { sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id, actor_name: state.template.name,
      feature_id: "adrenaline-rush", resource_remaining: state.resources["adrenaline-rush"], movement_ft: 0,
      animation: "dash", description: `${state.template.name} uses Adrenaline Rush; Dash movement is abstracted by fixed Pit formation.` };
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Support hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
    const existing = () => new Set(hooks.abilitiesFor(phase).map((item) => item.id));

    if (!existing().has("second-wind")) hooks.registerAbility(phase, {
      id: "second-wind", priority: 20, rulesets: ["2014", "2024"],
      appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "beforeEscape",
      resolve: ({ sequence, round, member, setup }) => {
        const wind = secondWind(sequence, round, member);
        if (!wind) return null;
        const events = [wind]; let nextSequence = sequence + 1;
        const shift = window.IRON_PIT_BROWSER_TACTICAL_SHIFT?.resolve(nextSequence, round, member, setup);
        if (shift) {
          events.push(shift); nextSequence += 1;
          window.IRON_PIT_BROWSER_PALADIN_AURAS_2014?.sync(setup);
        }
        return { events, sequence: nextSequence, claimed: true };
      },
    });

    if (!existing().has("adrenaline-rush")) hooks.registerAbility(phase, {
      id: "adrenaline-rush", priority: 30, rulesets: ["2024"],
      appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "afterEscape",
      resolve: ({ sequence, round, member }) => {
        const event = adrenaline(sequence, round, member);
        return event ? { events: [event], sequence: sequence + 1, claimed: true } : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_SUPPORT = { adrenaline, resolve, secondWind, installAbilityHooks };
})();
