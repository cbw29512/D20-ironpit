(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const EFFECT_SIZE = "medium";

  function effectPosition(origin, originSize, target, setup, movementFt, reachFt) {
    try {
      const map = setup.map_definition;
      const targetPosition = target.state.position;
      if (!map || !targetPosition) {
        throw new Error("Persistent spell attacks require authoritative grid state.");
      }
      const candidates = [];
      for (let x = 0; x < map.width_squares; x += 1) {
        for (let y = 0; y < map.height_squares; y += 1) {
          const point = { x, y };
          const moved = G().footprintDistanceFt(origin, originSize, point, EFFECT_SIZE);
          if (moved > movementFt) continue;
          const distance = G().footprintDistanceFt(
            point,
            EFFECT_SIZE,
            targetPosition,
            target.state.template.size,
          );
          if (distance <= reachFt) candidates.push({ point, moved, x, y });
        }
      }
      candidates.sort((a, b) => a.moved - b.moved || a.y - b.y || a.x - b.x);
      return candidates[0] || null;
    } catch (error) {
      console.error("Browser persistent spell position search failed", {
        target: target?.combatant_id,
        error,
      });
      throw error;
    }
  }

  function activeState(member, action, round) {
    try {
      member.state.persistent_spell_attacks = (member.state.persistent_spell_attacks || [])
        .filter((item) => round < item.expires_round);
      return member.state.persistent_spell_attacks
        .find((item) => item.action_id === action.id) || null;
    } catch (error) {
      console.error("Browser persistent spell state lookup failed", {
        combatant: member?.combatant_id,
        error,
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
        combatant: member?.combatant_id,
        error,
      });
      throw error;
    }
  }

  function attackForSlot(action, slotLevel, repeat) {
    try {
      const extraDice = Math.max(
        0,
        Math.floor(
          (slotLevel - action.attack.level) / (action.upcastIntervalLevels || 1),
        ),
      );
      return {
        ...action.attack,
        level: repeat ? 0 : slotLevel,
        range: repeat ? action.attackReachFt : action.attack.range,
        damageDiceCount: action.attack.damageDiceCount + extraDice,
      };
    } catch (error) {
      console.error("Browser persistent spell scaling failed", {
        action: action?.id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_PERSISTENT_SPELL_ATTACK_SUPPORT = {
    EFFECT_SIZE,
    activeState,
    attackForSlot,
    castSlotLevel,
    effectPosition,
  };
})();
