# Copilot Instructions

## The Inversion Principle

> "Invert, always invert." — Carl Jacobi, adopted by Charlie Munger

When reviewing code, don't just ask "Is this correct?" — invert: **"How could this fail?"**

Munger observed: "It is remarkable how much long-term advantage people like us have gotten by trying to be consistently not stupid, instead of trying to be very intelligent."

Apply this to code review:
- Instead of checking if error handling looks right, ask: "What inputs would bypass this error handling?"
- Instead of verifying the happy path works, ask: "What conditions would make this silently fail?"
- Instead of assuming tests are sufficient, ask: "What failure modes are NOT tested?"

As Munger put it: "All I want to know is where I'm going to die, so I'll never go there."

Find where the code could die. Then we won't go there.

## Review Focus

### Bugs (Primary Focus)
- Logic errors, off-by-one mistakes, incorrect conditionals
- Missing guards, unreachable code paths, incorrect branching
- Edge cases: null/empty/undefined inputs, error conditions, race conditions
- Security issues: injection, auth bypass, data exposure
- Error handling that swallows failures or throws unexpectedly

### Structure
- Does it follow existing patterns and conventions?
- Are there established abstractions it should use but doesn't?
- Excessive nesting that could be flattened

### Performance (Only if Obviously Problematic)
- O(n²) on unbounded data, N+1 queries, blocking I/O on hot paths

## Python Standards

- Type hints required on all functions
- Async/await for I/O operations
- Defensive error handling with clear, actionable messages
- PEP 257 docstrings for public functions/classes
- Prefer dataclasses over Pydantic when possible

## Testing Standards

- pytest with parameterization and fixtures
- Focus on critical paths and failure modes
- Add specs to mocks to verify correct attributes

## What NOT to Flag

- Style preferences unless clearly violating project conventions
- Hypothetical problems without realistic failure scenarios
- Pre-existing code that wasn't modified in this change
- Minor nitpicks that don't affect correctness or maintainability
