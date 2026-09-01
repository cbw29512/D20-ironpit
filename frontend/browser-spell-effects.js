/* GENERATED from canonical Python certified spell effects. Do not hand-edit. */
(() => {
  "use strict";
  const spells = [{"actionCost":"action","animation":"bless","concentration":true,"damageResistances":[],"durationMinutes":1,"id":"bless","level":1,"modifierEffects":[{"damageType":null,"diceCount":1,"diceSize":4,"flatBonus":0,"kind":"attack-roll-bonus-die"},{"damageType":null,"diceCount":1,"diceSize":4,"flatBonus":0,"kind":"saving-throw-bonus-die"}],"name":"Bless","priority":30,"range":30,"source":"SRD 5.2.1 Bless","targetCount":3,"targetPolicy":"friendly","temporaryHp":0,"temporaryHpPerSlotAbove":0},{"actionCost":"bonus_action","animation":"shield-of-faith","concentration":true,"damageResistances":[],"durationMinutes":10,"id":"shield-of-faith","level":1,"modifierEffects":[{"damageType":null,"diceCount":0,"diceSize":0,"flatBonus":2,"kind":"armor-class"}],"name":"Shield of Faith","priority":20,"range":60,"source":"SRD 5.2.1 p.162","targetCount":1,"targetPolicy":"self","temporaryHp":0,"temporaryHpPerSlotAbove":0}];
  window.IRON_PIT_BROWSER_SPELL_EFFECTS = Object.fromEntries(spells.map((item) => [item.id, item]));
})();
