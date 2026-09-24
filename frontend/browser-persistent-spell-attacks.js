(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_SPELL_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const S = () => window.IRON_PIT_BROWSER_PERSISTENT_SPELL_ATTACK_SUPPORT;

  function resolve(sequence, round, member, setup, turnKey) {
    try {
      if (!E().available(member.state, "bonus_action") || !member.state.position) return null;
      for (const action of member.state.template.persistent_spell_attack_actions || []) {
        const active = S().activeState(member, action, round);
        const origin = active ? active.position : member.state.position;
        const originSize = active ? S().EFFECT_SIZE : member.state.template.size;
        const movement = active ? action.moveFt : action.attack.range;
        for (const target of F().targetOrder(member, setup)) {
          const placement = S().effectPosition(
            origin,
            originSize,
            target,
            setup,
            movement,
            action.attackReachFt,
          );
          if (!placement) continue;
          const slotLevel = active
            ? active.slot_level
            : S().castSlotLevel(member, action, turnKey);
          if (slotLevel == null) continue;
          const attack = S().attackForSlot(action, slotLevel, Boolean(active));
          const distance = G().footprintDistanceFt(
            placement.point,
            S().EFFECT_SIZE,
            target.state.position,
            target.state.template.size,
          );
          const event = A().resolve(
            sequence,
            round,
            member,
            target,
            attack,
            setup,
            turnKey,
            { distanceOverrideFt: distance },
          );
          if (!active) {
            member.state.persistent_spell_attacks = member.state.persistent_spell_attacks
              .filter((item) => item.action_id !== action.id);
            member.state.persistent_spell_attacks.push({
              action_id: action.id,
              slot_level: slotLevel,
              position: placement.point,
              applied_round: round,
              expires_round: round + action.durationRounds,
            });
          } else {
            active.position = placement.point;
          }
          event.movement_ft = placement.moved;
          event.grid_position_after = { ...placement.point };
          return event;
        }
      }
      return null;
    } catch (error) {
      console.error("Browser persistent spell attack resolution failed", {
        combatant: member?.combatant_id,
        error,
      });
      throw error;
    }
  }

  function installAbilityHooks() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      if (!hooks) {
        throw new Error("Persistent spell attacks require browser-ability-hooks.js.");
      }
      const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
      if (hooks.abilitiesFor(phase).some((item) => item.id === "persistent-spell-attack")) {
        return;
      }
      hooks.registerAbility(phase, {
        id: "persistent-spell-attack",
        priority: 40,
        rulesets: ["2014"],
        appliesTo: (member, ctx) => ctx.bonusActionCheckpoint === "afterEscape"
          && (member.state.template.persistent_spell_attack_actions || []).length > 0,
        resolve: ({ sequence, round, member, setup, turnKey }) => {
          const event = resolve(sequence, round, member, setup, turnKey);
          return event
            ? { events: [event], sequence: sequence + 1, claimed: true }
            : null;
        },
      });
    } catch (error) {
      console.error("Persistent spell attack hook installation failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_PERSISTENT_SPELL_ATTACKS = {
    installAbilityHooks,
    resolve,
  };
})();
