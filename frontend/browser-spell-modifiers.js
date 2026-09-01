(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;

  function build(sourceId, targetId, spell, effect, index) {
    return {
      id: `${sourceId}:${spell.id}:${targetId}:${index}`,
      source_id: sourceId,
      source_effect_id: spell.id,
      kind: effect.kind,
      flat_bonus: effect.flatBonus || 0,
      dice_count: effect.diceCount || 0,
      dice_size: effect.diceSize || 0,
      damage_type: effect.damageType || null,
      target_id: targetId,
      concentration_required: Boolean(spell.concentration),
    };
  }

  function apply(owner, target, sourceId, targetId, spell, roundNumber, states = []) {
    const modifiers = (spell.modifierEffects || []).map((effect, index) => build(sourceId, targetId, spell, effect, index));
    if (spell.concentration) {
      if (!C()) throw new Error("Browser Concentration runtime is not loaded.");
      C().start(owner, sourceId, spell.id, roundNumber, states);
    }
    for (const modifier of modifiers) M().add(target, modifier);
    return modifiers;
  }

  window.IRON_PIT_BROWSER_SPELL_MODIFIERS = { apply, build };
})();
