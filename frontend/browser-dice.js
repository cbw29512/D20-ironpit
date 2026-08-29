(() => {
  "use strict";

  const UINT32_RANGE = 0x100000000;

  function roll(sides) {
    try {
      if (!Number.isInteger(sides) || sides < 2) throw new RangeError("Die sides must be an integer >= 2.");
      if (!globalThis.crypto?.getRandomValues) throw new Error("Web Crypto RNG is unavailable.");

      // Rejection sampling avoids modulo bias while keeping the source cryptographically strong.
      const limit = UINT32_RANGE - (UINT32_RANGE % sides);
      const buffer = new Uint32Array(1);
      let value;
      do {
        globalThis.crypto.getRandomValues(buffer);
        value = buffer[0];
      } while (value >= limit);
      return (value % sides) + 1;
    } catch (error) {
      console.error(`Secure d${sides} roll failed`, error);
      throw error;
    }
  }

  function rollMany(count, sides) {
    try {
      if (!Number.isInteger(count) || count < 1) throw new RangeError("Dice count must be positive.");
      return Array.from({ length: count }, () => roll(sides));
    } catch (error) {
      console.error("Secure dice pool failed", error);
      throw error;
    }
  }

  window.IRON_PIT_DICE = { roll, rollMany };
})();
