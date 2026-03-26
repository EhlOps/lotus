## Coding Standards: Refactor

You are refactoring existing code.

1. **Zero behavior changes.** Existing tests are the contract. If you need to
   change a test, STOP — you're changing behavior.
2. **Measure complexity before and after.** Run `radon cc <files> -a -nc`
   (Python). Complexity must decrease or stay flat.
3. **Reduce, don't rearrange.** Fewer lines, fewer branches, fewer abstractions.
4. **One transformation per issue.** Don't combine multiple refactors.
5. **DO NOT add or modify tests.**

## Process
1. Identify target code from the issue.
2. Measure "before" complexity.
3. Apply the refactor.
4. Full validation — every test passes WITHOUT modification.
5. Measure "after" complexity. Confirm ≤ before.
6. Review diff — purely structural, not behavioral.
