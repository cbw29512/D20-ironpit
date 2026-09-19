(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const IP = () => window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014;
  const M = () => window.IRON_PIT_BROWSER_MULTIATTACK;
  const A = () => window.IRON_PIT_BROWSER_AREA_SAVES;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const SV = () => window.IRON_PIT_BROWSER_SAVE_ACTION_POLICY;
  const U = () => window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION;
  const DG = () => window.IRON_PIT_BROWSER_DODGE;
  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_CHARGE;

  function oneEvent(event, sequence) {
    if (!event) throw new Error("Selected Main Action provider produced no event.");
    return { events: [event], sequence: sequence + 1 };
  }

  function install() {
    const selector = S();
    if (!selector) throw new Error("Core Main Action providers require browser-main-action-selection.js.");
    const K = selector.CATEGORIES;

    selector.registerProvider({
      id: "intimidating-presence-2014", category: K.INTIMIDATING_PRESENCE_2014, rulesets: ["2014"],
      discover: ({ member, setup }) => {
        const target = F().targetOrder(member, setup)[0] || null;
        return target && IP().canUse(member, target) ? { payload: { target } } : null;
      },
      resolve: ({ sequence, round, member }, candidate) =>
        oneEvent(IP().resolve(sequence, round, member, candidate.payload.target), sequence),
    });
    selector.registerProvider({
      id: "attack-action", category: K.ATTACK_ACTION, rulesets: ["2014", "2024"],
      discover: ({ member, setup }) => M().available(member, setup) ? { payload: {} } : null,
      resolve: ({ sequence, round, member, setup }) => M().resolveAttackAction(sequence, round, member, setup),
    });
    selector.registerProvider({
      id: "area-save", category: K.AREA_SAVE, rulesets: ["2014", "2024"],
      discover: ({ member, setup }) => {
        const selected = A().choose(member, setup);
        return selected ? { payload: { selected } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) =>
        A().resolve(sequence, round, member, setup, candidate.payload.selected),
    });
    selector.registerProvider({
      id: "save-action", category: K.SAVE_ACTION, rulesets: ["2014", "2024"],
      discover: ({ member, setup }) => {
        const selected = SV().choose(member, setup);
        return selected ? { payload: { selected } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const selected = candidate.payload.selected;
        const event = V().resolveAction(
          sequence, round, member, selected.target, selected.action, selected.distance, { setup },
        );
        return oneEvent(event, sequence);
      },
    });
    selector.registerProvider({
      id: "standard-attack", category: K.STANDARD_ATTACK, rulesets: ["2014", "2024"],
      discover: ({ member, setup }) => {
        const selected = E().available(member.state, "action") ? F().chooseStandardAttack(member, setup) : null;
        return selected ? { payload: { selected } } : null;
      },
      resolve: ({ sequence, round, member, setup, turnKey }, candidate) => {
        const choice = candidate.payload.selected;
        const pack = ST().packTactics(member, choice.target, setup);
        const opener = C()?.openingFeature?.(round, member, setup) || null;
        return U().resolve(
          sequence, round, member, choice.target, choice.attack, choice.distance, setup, turnKey,
          { advantage: pack ? 1 : 0, featureId: opener || (pack ? "pack-tactics" : null) },
        );
      },
    });
    selector.registerProvider({
      id: "dodge", category: K.DODGE, rulesets: ["2014", "2024"],
      discover: ({ member }) => E().available(member.state, "action") ? { payload: {} } : null,
      resolve: ({ sequence, round, member }) => oneEvent(DG().take(sequence, round, member), sequence),
    });
  }

  window.IRON_PIT_BROWSER_MAIN_ACTION_CORE_PROVIDERS = { install };
  if (window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION) install();
  else (window.IRON_PIT_PENDING_MAIN_ACTION_PROVIDER_INSTALLERS ||= []).push(install);
})();
