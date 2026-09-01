(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  function concentrationDc(damageTaken) {
    if (!Number.isInteger(damageTaken) || damageTaken < 0) throw new Error("Concentration damage must be a nonnegative integer.");
    return Math.min(30, Math.max(10, Math.floor(damageTaken / 2)));
  }

  function affected(owner, states = []) {
    const result = [...states];
    if (!result.includes(owner)) result.push(owner);
    return result;
  }

  function end(owner, states = []) {
    const current = owner.concentration;
    if (!current) return false;
    M().removeSource(affected(owner, states), current.source_id, current.effect_id, true);
    owner.concentration = null;
    return true;
  }

  function start(owner, sourceId, effectId, roundNumber, states = [], expiresRound = null) {
    if (owner.is_dead || Q().incapacitated(owner)) throw new Error("An Incapacitated or dead creature cannot start Concentration.");
    if (expiresRound != null && (!Number.isInteger(expiresRound) || expiresRound <= roundNumber)) throw new Error("Concentration expiry must be after the start round.");
    end(owner, states);
    owner.concentration = { source_id: sourceId, effect_id: effectId, started_round: roundNumber, expires_round: expiresRound };
    return owner.concentration;
  }

  function endIfIncapacitated(owner, states = []) {
    if (!owner.concentration || (!owner.is_dead && !Q().incapacitated(owner))) return false;
    return end(owner, states);
  }

  function endIfExpired(owner, roundNumber, states = []) {
    const current = owner.concentration;
    if (!current || current.expires_round == null || roundNumber < current.expires_round) return false;
    return end(owner, states);
  }

  function resolveDamage(owner, damageTaken, states = []) {
    if (!Number.isInteger(damageTaken) || damageTaken < 0) throw new Error("Concentration damage must be a nonnegative integer.");
    if (!owner.concentration || damageTaken === 0) return null;
    if (owner.is_dead || Q().incapacitated(owner)) {
      end(owner, states);
      return { dc: null, roll: null, succeeded: false, ended: true, reason: "incapacitated-or-dead" };
    }
    if (!V()) throw new Error("Browser saving-throw runtime is not loaded.");
    const dc = concentrationDc(damageTaken);
    const save = V().resolveSavingThrow(owner, "constitution", dc);
    if (!save.succeeded) end(owner, states);
    return { dc, roll: save.roll, succeeded: save.succeeded, ended: !save.succeeded, reason: "damage" };
  }

  window.IRON_PIT_BROWSER_CONCENTRATION = { concentrationDc, end, endIfExpired, endIfIncapacitated, resolveDamage, start };
})();
