((root) => {
  "use strict";

  const human = `<circle cx="90" cy="42" r="22"/><line x1="90" y1="64" x2="90" y2="132"/><line x1="90" y1="82" x2="53" y2="111"/><line x1="90" y1="82" x2="128" y2="108"/><line x1="90" y1="132" x2="61" y2="188"/><line x1="90" y1="132" x2="121" y2="188"/>`;
  const shield = `<circle class="shield" cx="49" cy="113" r="18"/><line class="shield-mark" x1="49" y1="99" x2="49" y2="127"/>`;
  const sword = `<g class="weapon sword"><line x1="128" y1="108" x2="148" y2="82"/><line class="guard-mark" x1="139" y1="91" x2="154" y2="102"/><path class="blade" d="M148 82 L166 48 L161 86 Z"/></g>`;
  const bow = `<g class="weapon bow"><path d="M133 76 Q164 108 133 140"/><line x1="133" y1="76" x2="133" y2="140"/><line x1="133" y1="108" x2="161" y2="108"/><path class="blade" d="M161 108 L151 102 L151 114 Z"/></g>`;
  const staff = `<g class="weapon staff"><line x1="128" y1="108" x2="158" y2="48"/></g>`;

  const figures = {
    barbarian: `${human}<path class="wild-hair" d="M67 40 L58 24 L73 29 L82 16 L91 28 L103 16 L108 31 L123 26 L113 45"/><g class="weapon greataxe"><line x1="53" y1="111" x2="153" y2="66"/><path class="blade" d="M146 67 Q171 41 177 63 Q170 88 147 82 Z"/></g>`,
    bard: `${human}<path class="feather" d="M104 25 Q128 7 121 40"/><ellipse class="instrument" cx="137" cy="111" rx="20" ry="27"/><line x1="126" y1="92" x2="159" y2="60"/><line x1="120" y1="111" x2="151" y2="111"/>`,
    cleric: `${human}${shield}<g class="weapon mace"><line x1="128" y1="108" x2="154" y2="66"/><circle cx="159" cy="59" r="10"/></g><path class="holy-mark" d="M90 76 V101 M78 88 H102"/>`,
    druid: `${human}${staff}<path class="leaf" d="M158 48 Q171 32 178 51 Q167 57 158 48 M153 58 Q139 43 136 61 Q147 67 153 58"/>`,
    fighter: `${human}${sword}${shield}`,
    monk: `${human}<g class="weapon staff"><line x1="42" y1="151" x2="153" y2="70"/></g><path class="wrap" d="M45 108 L60 119 M119 104 L135 114"/>`,
    paladin: `${human}${sword}${shield}<path class="holy-mark" d="M49 103 V123 M39 113 H59"/>`,
    ranger: `${human}${bow}<path class="cloak" d="M69 70 Q48 103 61 145"/>`,
    rogue: `${human}<path class="hood" d="M67 48 Q90 11 113 48"/><g class="weapon shortblade"><line x1="128" y1="108" x2="153" y2="78"/><path class="blade" d="M153 78 L165 57 L160 82 Z"/></g><line class="dagger" x1="49" y1="110" x2="31" y2="91"/>`,
    sorcerer: `${human}<circle class="magic-orb" cx="151" cy="83" r="14"/><path class="magic-mark" d="M151 61 L157 75 L173 78 L160 88 L164 104 L151 95 L138 104 L142 88 L129 78 L145 75 Z"/>`,
    warlock: `${human}<g class="weapon rod"><line x1="128" y1="108" x2="154" y2="62"/></g><path class="eldritch" d="M154 62 Q177 45 169 80 Q145 91 154 62"/>`,
    wizard: `${human}${staff}<path class="hat" d="M65 43 L91 6 L116 43 Z M59 46 H121"/><path class="book" d="M45 103 Q58 96 70 107 V130 Q58 119 45 126 Z"/>`,
    goblin: `<circle cx="90" cy="58" r="19"/><path class="ear" d="M72 55 L48 45 L70 68 M108 55 L132 45 L110 68"/><line x1="90" y1="77" x2="90" y2="136"/><line x1="90" y1="92" x2="52" y2="116"/><line x1="90" y1="92" x2="128" y2="112"/><line x1="90" y1="136" x2="61" y2="184"/><line x1="90" y1="136" x2="120" y2="184"/><g class="weapon"><path d="M128 112 Q151 91 159 62"/></g><circle class="shield" cx="48" cy="117" r="18"/>`,
    bandit: `${human}<path class="bandana" d="M68 38 Q90 23 112 38 M110 38 L132 27"/><g class="weapon"><path d="M128 108 Q153 94 159 66"/></g>`,
    guard: `${human}<path class="helmet" d="M67 42 Q90 18 113 42 M67 42 L113 42"/><g class="weapon spear"><line x1="128" y1="109" x2="165" y2="46"/><path class="blade" d="M165 46 L160 60 L174 55 Z"/></g>${shield}`,
  };

  const classKeys = ["barbarian", "bard", "cleric", "druid", "fighter", "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"];
  function figureKey(template) {
    try {
      const archetype = String(template?.archetype || "").toLowerCase();
      if (archetype.includes("goblin")) return "goblin";
      if (archetype.includes("bandit")) return "bandit";
      if (archetype.includes("guard")) return "guard";
      return classKeys.find((key) => archetype.includes(key)) || "fighter";
    } catch (error) { console.error("Figure identity resolution failed", error); return "fighter"; }
  }

  function render(slot, template) {
    try {
      const svg = document.querySelector(`#${slot}`);
      if (!svg) return;
      const key = figureKey(template);
      svg.className.baseVal = "stick";
      svg.dataset.figure = key;
      svg.innerHTML = figures[key] || figures.fighter;
      svg.setAttribute("aria-label", `${template.name}, ${template.archetype}`);
    } catch (error) { console.error("Combatant figure render failed", error); }
  }

  root.createIronPitFigureView = () => ({ render });
})(typeof window !== "undefined" ? window : globalThis);
