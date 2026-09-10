# Per-package definition of done

Work through this before reporting a package as migrated.

## Contract

- [ ] Every entity exported by the `.ads` exists in the header.
- [ ] Nothing private to the body leaked into the header.
- [ ] Every exception the package can raise is declared and reachable.
- [ ] Every subtype constraint has an explicit check with the same
      observable effect as the Ada run-time check.

## Semantics

- [ ] No fixed point or integer type was translated to `double`.
- [ ] Integer division, rounding and truncation match the Ada behaviour.
- [ ] Loop and iteration order match, including reverse loops and nested
      loop order (it determines the order of emitted output).
- [ ] Array index base (1 vs 0) handled at every conversion site.
- [ ] Exception message text is byte-identical.
- [ ] Uninitialised values: anything Ada default-initialises is initialised
      in C++ too.

## Build and test

- [ ] New sources listed in `cpp/CMakeLists.txt`.
- [ ] Compiles with `-Wall -Wextra` (or `/W4`) with no new warnings.
- [ ] Full parity suite green — not just the case related to this package.
- [ ] No golden file, Ada source, or test was modified.

## Review

- [ ] The C++ can be diffed against the Ada unit by name.
- [ ] Any construct that could not be translated faithfully is written up,
      with the Ada file and line.
