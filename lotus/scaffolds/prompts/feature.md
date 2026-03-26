## Coding Standards: Feature Implementation

You are implementing a NEW feature.

1. **Additive, not invasive.** Create new files/functions. Only modify existing
   code at small integration points (route registration, imports, call sites).
2. **Interface-first.** Define public signatures before implementation.
3. **Test every acceptance criterion.** Each criterion → at least one test.
4. **No opportunistic refactoring.** If it's ugly, leave it.

## Process
1. Read acceptance criteria.
2. Find minimal integration points in existing code.
3. Write new code in new files where possible.
4. Write tests covering every criterion.
5. Wire into existing code at integration points.
6. Run full validation. Review diff — revert anything unrelated.
