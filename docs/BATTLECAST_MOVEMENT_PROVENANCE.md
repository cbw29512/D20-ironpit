# BattleCast movement provenance

Iron Pit uses BattleCast as a reference implementation for tactical-grid movement because its browser movement behavior matches the approved Iron Pit VTT direction.

## Upstream source

- Repository: `bjedrzejewski/battlecast-engine`
- Pinned upstream commit: `ffe036c758f18e772a808f538fe3baa845b9bcc0`
- License: MIT
- Copyright: Copyright (c) 2026 Bartosz Jedrzejewski

Relevant upstream files at the pinned commit:

- `src/engine/combat-geometry.ts`
- `src/engine/ai-movement.ts`
- `src/engine/ai-movement-evaluator.ts`

## Reuse boundary

Iron Pit may adapt BattleCast's movement/pathfinding algorithms while keeping Iron Pit's own schemas, rules contracts, event stream, action economy, conditions, creature-space passage rules, movement modes, and card-token presentation.

The reusable movement ideas include:

- Chebyshev 5-foot grid distance;
- footprint-aware collision and target distance;
- A* pathfinding over eight-direction movement;
- searching beyond the current turn's movement budget and returning only the affordable path prefix;
- best-effort partial paths when the ideal destination is unreachable;
- prevention of illegal diagonal corner cutting;
- separation of movement legality/pathfinding from AI destination policy.

Monster names, class names, and card identities never select movement rules.

## MIT notice

MIT License

Copyright (c) 2026 Bartosz Jedrzejewski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
