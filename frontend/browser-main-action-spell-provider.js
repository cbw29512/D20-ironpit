(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const O = () => window.IRON_PIT_BROWSER_SPELL_OFFENSE;

  function install() {
    const selector = S();
    if (!selector) throw new Error("Spell Main Action provider requires browser-main-action-selection.js.");
    selector.registerProvider({
      id: "spell-offense",
      category: selector.CATEGORIES.SPELL_OFFENSE,
      rulesets: ["2014", "2024"],
      discover: ({ member, setup, turnKey }) => {
        const selected = O().choose(member, setup, turnKey);
        return selected ? { payload: { selected } } : null;
      },
      resolve: ({ sequence, round, member, setup, turnKey }, candidate) =>
        O().resolveChoice(sequence, round, member, setup, turnKey, candidate.payload.selected),
    });
  }

  window.IRON_PIT_BROWSER_MAIN_ACTION_SPELL_PROVIDER = { install };
  if (window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION) install();
  else (window.IRON_PIT_PENDING_MAIN_ACTION_PROVIDER_INSTALLERS ||= []).push(install);
})();
