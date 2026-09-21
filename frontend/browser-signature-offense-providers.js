(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const AS = () => window.IRON_PIT_BROWSER_AREA_SAVES;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const BOTH = Object.freeze(["2014", "2024"]);

  const memberById = (setup, id) => [...setup.heroes, ...setup.monsters]
    .find((member) => member.combatant_id === id) || null;
  const actionById = (member, id) => (member.state.template.saving_throw_actions || [])
    .find((action) => action.id === id) || null;

  function singleChoice(member, setup) {
    if (!E().available(member.state, "action")) return null;
    for (const target of F().targetOrder(member, setup)) {
      for (const action of member.state.template.saving_throw_actions || []) {
        if (!action.resourceId || action.area) continue;
        const distance = F().saveDistance(member, target, action.range);
        if (V().legalAction(action, target, distance)) return { target, action, distance };
      }
    }
    return null;
  }

  function install() {
    const selector = S();
    if (!selector) throw new Error("Signature offense providers require Main Action selection.");
    selector.registerProvider({
      id: "signature-area-save", category: selector.CATEGORIES.SIGNATURE_AREA_SAVE, rulesets: BOTH,
      discover: ({ member, setup }) => {
        if (!E().available(member.state, "action")) return null;
        const selected = AS()?.choose(member, setup, true) || null;
        return selected ? { payload: { selected } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const result = AS().resolve(sequence, round, member, setup, candidate.payload.selected);
        if (!result) throw new Error("Signature area-save candidate became illegal before resolution.");
        return { events: result.events, sequence: result.sequence };
      },
    });
    selector.registerProvider({
      id: "signature-save-action", category: selector.CATEGORIES.SIGNATURE_SAVE_ACTION, rulesets: BOTH,
      discover: ({ member, setup }) => {
        const selected = singleChoice(member, setup);
        return selected ? { payload: {
          targetId: selected.target.combatant_id, actionId: selected.action.id, distance: selected.distance,
        } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const target = memberById(setup, candidate.payload.targetId);
        const action = actionById(member, candidate.payload.actionId);
        if (!target || !action) throw new Error("Signature save-action candidate target/action is unavailable.");
        const event = V().resolveAction(sequence, round, member, target, action, candidate.payload.distance, { setup });
        const next = sequence + 1;
        return DR() ? DR().chain(next, round, member, event, setup) : { events: [event], sequence: next };
      },
    });
  }

  install();
  window.IRON_PIT_BROWSER_SIGNATURE_OFFENSE_PROVIDERS = { install, singleChoice };
})();
