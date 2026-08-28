((root) => {
  "use strict";

  const human = `
    <circle cx="90" cy="42" r="22"/><line x1="90" y1="64" x2="90" y2="132"/>
    <line x1="90" y1="82" x2="52" y2="112"/><line x1="90" y1="82" x2="128" y2="108"/>
    <line x1="90" y1="132" x2="60" y2="188"/><line x1="90" y1="132" x2="122" y2="188"/>`;

  const figures = {
    fighter: `${human}
      <g class="weapon"><line x1="128" y1="108" x2="156" y2="64"/><line x1="148" y1="66" x2="166" y2="78"/></g>
      <circle class="shield" cx="47" cy="113" r="22"/>`,
    rogue: `${human}
      <path class="hood" d="M67 47 Q90 12 113 47"/>
      <g class="weapon"><path d="M133 80 Q158 108 133 136"/><line x1="133" y1="80" x2="133" y2="136"/></g>
      <line class="dagger" x1="48" y1="111" x2="30" y2="91"/>`,
    goblin: `
      <circle cx="90" cy="58" r="19"/><path class="ear" d="M72 55 L48 45 L70 68 M108 55 L132 45 L110 68"/>
      <line x1="90" y1="77" x2="90" y2="136"/><line x1="90" y1="92" x2="52" y2="116"/><line x1="90" y1="92" x2="128" y2="112"/>
      <line x1="90" y1="136" x2="61" y2="184"/><line x1="90" y1="136" x2="120" y2="184"/>
      <g class="weapon"><path d="M128 112 Q153 88 160 62"/><line x1="151" y1="70" x2="165" y2="78"/></g>
      <circle class="shield" cx="48" cy="117" r="19"/>`,
    bandit: `${human}
      <path class="bandana" d="M68 38 Q90 23 112 38 M110 38 L132 27 M111 42 L136 45"/>
      <g class="weapon"><line x1="126" y1="108" x2="158" y2="108"/><path d="M139 94 Q158 108 139 122"/><line x1="139" y1="94" x2="139" y2="122"/></g>`,
    guard: `${human}
      <path class="helmet" d="M67 42 Q90 18 113 42 M67 42 L113 42"/>
      <g class="weapon"><line x1="128" y1="109" x2="165" y2="45"/><path d="M165 45 L160 59 L174 55 Z"/></g>
      <circle class="shield" cx="47" cy="113" r="24"/><line class="shield-mark" x1="47" y1="94" x2="47" y2="132"/>`,
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
