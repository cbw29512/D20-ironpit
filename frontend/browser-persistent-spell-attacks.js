(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_SPELL_ATTACK;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const EFFECT_SIZE = "medium";

  function effectPosition(origin, originSize, target, setup, movementFt, reachFt) {
    try {
      const map = setup.map_definition;
      const targetPosition = target.state.position;
      if (!map || !targetPosition) throw new Error("Persistent spell attacks require authoritative grid state.");
      const candidates = [];
      for (let x = 0; x < map.width_squares; x += 1) {
        for (let y = 0; y < map.height_squares; y += 1) {
          const point = { x, y };
          const moved = G().footprintDistanceFt(origin, originSize, point, EFFECT_SIZE);
          if (moved > movementFt) continue;
          const distance = G().footprintDistanceFt(
            point, EFFECT_SIZE, targetPosition, target.state.template.size,
          );
          if (distance <= reachFt) candidates.push({ point, moved, x, y });
        }
      }
      candidates.sort((a, b) => a.moved - b.moved || a.y - b.y || a.x - b.x);
      return candidates[0] || null;
    } catch (error) {
      console.error("Browser persistent spell position search failed", {
        target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  function activeState(member, action, round) {
    try {
      member.state.persistent_spell_attacks = (member.state.persistent_spell_attacks || [])
        .filter((item) => round < item.expires_round);
      return member.state.persistent_spell_attacks.find((item) => item.action_id === action.id) || null;
    } catch (error) {
      console.error("Browser persistent spell state lookup failed", {
        combatant: member?.combatant_id, error,
      });
      throw error;
    }
  }

  function castSlotLevel(member, action, turnKey) {
    try {
      if (!C().slotSpellAvailable(member.state, turnKey)) return null;
      const levels = Object.entries(member.state.resources || {})
        .filter(([id, uses]) => id.startsWith("spell-slot-") && uses > 0)
        .map(([id]) => Number.parseInt(id.slice("spell-slot-".length), 10))
        .filter((level) => Number.isInteger(level) && level >= action.attack.level)
        .sort((a, b) => a - b);
      return levels[0] ?? null;
    } catch (error) {
      console.error("Browser persistent spell slot lookup failed", {
        combatant: member?.combatant_id, error,
      });
      throw error;
    }
  }

  function attackForSlot(action, slotLevel, repeat) {
    try {
      const extraDice = Math.max(
        0,
        Math.floor((slotLevel - action.attack.level) / (action.upcastIntervalLevels || 1)),
      );
      return {
        ...action.attack,
        level: repeat ? 0 : slotLevel,
        range: repeat ? action.attackReachFt : action.attack.range,
        damageDiceCount: action.attack.damageDiceCount + extraDice,
      };
    } catch (error) {
      console.error("Browser persistent spell scaling failed", { action: action?.id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, turnKey) {
    try {
      if (!E().available(member.state, "bonus_action") || !member.state.position) return null;
      for (const action of member.state.template.persistent_spell_attack_actions || []) {
        const active = activeState(member, action, round);
        const origin = active ? active.position : member.state.position;
        const originSize = active ? EFFECT_SIZE : member.state.template.size;
        const movement = active ? action.moveFt : action.attack.range;
        for (const target of F().targetOrder(member, setup)) {
          const placement = effectPosition(
            origin, originSize, target, setup, movement, action.attackReachFt,
          );
          if (!placement) continue;
          const slotLevel = active ? active.slot_level : castSlotLevel(member, action, turnKey);
          if (slotLevel == null) continue;
          const attack = attackForSlot(action, slotLevel, Boolean(active));
          const distance = G().footprintDistanceFt(
            placement.point, EFFECT_SIZE, target.state.position, target.state.template.size,
          );
          const event = A().resolve(
            sequence, round, member, target, attack, setup, turnKey,
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
        combatant: member?.combatant_id, error,
      });
      throw error;
    }
  }

  function installAbilityHooks() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      if (!hooks) throw new Error("Persistent spell attacks require browser-ability-hooks.js.");
      const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
      if (hooks.abilitiesFor(phase).some((item) => item.id === "persistent-spell-attack")) return;
      hooks.registerAbility(phase, {
        id: "persistent-spell-attack",
        priority: 40,
        rulesets: ["2014"],
        appliesTo: (member, ctx) => ctx.bonusActionCheckpoint === "afterEscape"
          && (member.state.template.persistent_spell_attack_actions || []).length > 0,
        resolve: ({ sequence, round, member, setup, turnKey }) => {
          const event = resolve(sequence, round, member, setup, turnKey);
          return event ? { events: [event], sequence: sequence + 1, claimed: true } : null;
        },
      });
    } catch (error) {
      console.error("Persistent spell attack hook installation failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_PERSISTENT_SPELL_ATTACKS = {
    activeState, attackForSlot, castSlotLevel, effectPosition, installAbilityHooks, resolve,
  };
})();
