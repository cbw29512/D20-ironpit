((root) => {
  "use strict";

  const human = `
    <circle cx="90" cy="42" r="22"/><line x1="90" y1="64" x2="90" y2="132"/>
    <line x1="90" y1="82" x2="53" y2="111"/><line x1="90" y1="82" x2="128" y2="108"/>
    <line x1="90" y1="132" x2="61" y2="188"/><line x1="90" y1="132" x2="121" y2="188"/>`;

  const figures = {
    fighter: `${human}
      <g class="weapon sword"><line x1="128" y1="108" x2="148" y2="82"/><line class="guard-mark" x1="139" y1="91" x2="154" y2="102"/><path class="blade" d="M148 82 L166 48 L161 86 Z"/></g>
      <circle class="shield" cx="49" cy="113" r="18"/><line class="shield-mark" x1="49" y1="99" x2="49" y2="127"/>`,
    rogue: `${human}
      <path class="hood" d="M67 48 Q90 11 113 48"/>
      <g class="weapon bow"><path d="M133 76 Q164 108 133 140"/><line x1="133" y1="76" x2="133" y2="140"/><line x1="133" y1="108" x2="161" y2="108"/><path class="blade" d="M161 108 L151 102 L151 114 Z"/></g>
      <line class="dagger" x1="49" y1="110" x2="31" y2="91"/>`,
    goblin: `
      <circle cx="90" cy="58" r="19"/><path class="ear" d="M72 55 L48 45 L70 68 M108 55 L132 45 L110 68"/>
      <line x1="90" y1="77" x2="90" y2="136"/><line x1="90" y1="92" x2="52" y2="116"/><line x1="90" y1="92" x2="128" y2="112"/>
      <line x1="90" y1="136" x2="61" y2="184"/><line x1="90" y1="136" x2="120" y2="184"/>
      <g class="weapon"><path d="M128 112 Q151 91 159 62"/><path class="blade" d="M159 62 L170 48 L166 68 Z"/></g>
      <circle class="shield" cx="48" cy="117" r="18"/>`,
    bandit: `${human}
      <path class="bandana" d="M68 38 Q90 23 112 38 M110 38 L132 27 M111 42 L136 45"/>
      <g class="weapon scimitar"><line x1="128" y1="108" x2="143" y2="100"/><path class="blade" d="M143 100 Q170 86 168 58 Q158 79 139 87"/></g>
      <line class="dagger" x1="53" y1="111" x2="36" y2="94"/>`,
    guard: `${human}
      <path class="helmet" d="M67 42 Q90 18 113 42 M67 42 L113 42"/>
      <g class="weapon spear"><line x1="128" y1="109" x2="165" y2="46"/><path class="blade" d="M165 46 L160 60 L174 55 Z"/></g>
      <circle class="shield" cx="48" cy="113" r="21"/><line class="shield-mark" x1="48" y1="96" x2="48" y2="130"/>`,
  };

  function figureKey(template) {
    try {
      const explicit = template?.visual?.body_style;
      if (figures[explicit]) return explicit;
      const archetype = String(template?.archetype || "").toLowerCase();
      if (archetype.includes("goblin")) return "goblin";
      if (archetype.includes("rogue")) return "rogue";
      if (archetype.includes("bandit")) return "bandit";
      if (archetype.includes("guard")) return "guard";
      return "fighter";
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
