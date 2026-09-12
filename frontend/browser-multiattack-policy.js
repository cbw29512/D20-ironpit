(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;

  function expandedSlots(definition) {
    const slots = definition.slots || [], policy = definition.policy;
    if (!policy || policy.repeatSlotIndex == null) return slots.map((slot, index) => ({ index, slot }));
    let repeats = 0;
    for (let index = 0; index < (policy.repeatDiceCount || 0); index += 1) repeats += D().roll(policy.repeatDiceSize);
    return slots.flatMap((slot, index) => Array.from(
      { length: index === policy.repeatSlotIndex ? repeats : 1 },
      () => ({ index, slot }),
    ));
  }

  function allowed(definition, index, previousEvent) {
    const required = definition.policy?.requiresPreviousHitSlots || [];
    return !required.includes(index) || previousEvent?.hit === true;
  }

  function requiredTargetId(definition, index, previousEvent) {
    const same = definition.policy?.sameTargetAsPreviousSlots || [];
    return same.includes(index) ? previousEvent?.target_id || null : null;
  }

  function filteredSlot(definition, data, usedAttackIds) {
    if (!definition.policy?.distinctAttackIds) return data;
    return { ...data, attackIds: data.attackIds.filter((id) => !usedAttackIds.has(id)) };
  }

  window.IRON_PIT_BROWSER_MULTIATTACK_POLICY = { allowed, expandedSlots, filteredSlot, requiredTargetId };
})();
