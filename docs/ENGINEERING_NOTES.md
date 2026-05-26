# Engineering Notes

This project keeps the decision path visible: diagnostics are implemented as deterministic rules, tests document the expected behavior, and runtime output is redacted before it is shown in the demo.

## Practical Approach

- Start with deterministic checks.
- Write regression tests for each rule.
- Keep suggestions tied to visible evidence.
- Document the tradeoffs before expanding the feature.

## Why This Is Better Than Black-Box Magic

Recruiters and engineering teams can inspect:

- what the analyzer checks;
- what evidence it uses;
- what suggestion it returns;
- which tests protect it from regressions.

## Future Explanation Layer

Any future explanation provider should stay optional:

- deterministic diagnostic first;
- plain-language explanation second;
- original evidence always visible;
- no hidden keyword stuffing;
- no fake claims about unsupported frameworks.
