## Coding Standards: Bug Fix

You are fixing a bug.

1. **Reproduce first.** Write a failing test before any fix. This is your
   regression test.
2. **Minimal diff.** One-line fixes are ideal. If > 20 lines of logic, stop
   and reconsider — you may be treating a symptom.
3. **No collateral changes.** Don't fix other bugs or refactor adjacent code.
4. **Root cause, not band-aid.** Don't null-check around a null — find why
   it's null.

## Process
1. Understand expected vs actual behavior.
2. Find the code path.
3. Write a failing test that reproduces the bug.
4. Fix the root cause. Keep it minimal.
5. Verify the test passes.
6. Full validation. Confirm nothing else broke.
