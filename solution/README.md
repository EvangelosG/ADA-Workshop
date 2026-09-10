# Solution — spoilers

Do not open during the lab.

- `ada-to-cpp-migration/` — a finished version of the skill attendees build.
  To use it, copy the folder to `.agents/skills/ada-to-cpp-migration/` at the
  repo root. It is kept here so Devin Desktop does not discover it mid-lab.
- `cpp/` — a completed migration that passes all five parity cases. Its
  layout matches `cpp/`, so the sources can be dropped straight in.

```bash
cmake -S solution/cpp -B solution/cpp/build
cmake --build solution/cpp/build
ctest --test-dir solution/cpp/build --output-on-failure
```
