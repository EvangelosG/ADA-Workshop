# Ada to C++ idiom map

Consult this before translating; consult it again when a parity case fails.
The entries marked **trap** are the ones that compile cleanly and produce the
wrong answer.

## Program structure

| Ada | C++ |
| --- | --- |
| `package P` spec (`.ads`) | `include/p.hpp`, `namespace p { ... }` |
| `package body P` (`.adb`) | `src/p.cpp` |
| child package `P.C` | nested namespace `p::c`, `include/p/c.hpp` |
| `private` part of a spec | private members / anonymous namespace in the `.cpp` |
| nested subprogram | file-local function in an anonymous namespace |
| `with P; use P;` | `#include "p.hpp"` (+ `using namespace p;` sparingly) |
| `pragma Unreferenced (X)` | `(void)x;` or an unnamed parameter |

## Types

| Ada | C++ |
| --- | --- |
| `type T is range 1 .. 99` | `using T = int` plus an explicit range check at every point a value of the type is produced — input, arithmetic results, conversions |
| `subtype S is T range A .. B` | same; the check does not come for free |
| enumeration type | `enum class` |
| `type R is record ... end record` | `struct` |
| discriminated record with a variant part | `std::variant` of per-discriminant structs, or a class hierarchy |
| `array (Positive range <>) of T` | `std::vector<T>` (**trap**: Ada arrays are commonly 1-based) |
| fixed length `String (1 .. N)` | `std::string` + explicit truncation to `N` |
| `access all T'Class` | `T*` / `std::unique_ptr<T>` — decide ownership explicitly |
| abstract tagged type + primitives | abstract class + virtual member functions |
| `overriding function` | `override` |
| generic package / subprogram | template (function template is usually enough) |
| `with function F (...) return B` generic formal | template parameter, or `std::function` when the indirection is required |

## Fixed point — the highest risk area

**trap**: `type Celsius is delta 0.1 digits 6` is *decimal* fixed point. It is
exact; `double` is not. Translating it to `double` will drift and produce
mismatched output that looks like a rounding "nit".

Represent it as a scaled integer (here: tenths of a degree) in a small wrapper
class. Then:

- Addition and subtraction map directly.
- `X / 2` on a decimal fixed point value truncates towards zero, which matches
  C++ integer division. Verify with a golden case that has a negative,
  odd-tenths value — this is exactly the sort of case a parity suite must
  contain.
- Formatting must be reimplemented from the scaled integer
  (`sign + magnitude/10 + "." + magnitude%10`), never with `printf("%.1f")`.

Binary fixed point (`delta 0.1` without `digits`) is *not* exact: its values
are multiples of a power of two. If the Ada uses it, reproduce the model
numbers or flag it rather than guessing.

## Control flow and errors

| Ada | C++ |
| --- | --- |
| `exception Invalid_Reading` | a class deriving from `std::runtime_error` |
| `raise E with "msg"` | `throw InvalidReading("msg")` (**trap**: the message text is often observable output — keep it byte-identical) |
| `exception when E : others =>` handler | `catch (const std::exception&)` |
| `Constraint_Error` from a subtype | explicit `if` + throw at the boundary |
| `Ada.Command_Line.Set_Exit_Status (2)` | `return 2;` from `main` |
| `for I in reverse A'Range loop` | reverse loop; with unsigned indices use the `for (i = n; i-- > 0;)` form |
| `exit when C` | `break` |

## I/O and text

| Ada | C++ |
| --- | --- |
| `Ada.Text_IO.Put_Line` | `std::cout << ... << "\n"` |
| `Put_Line (Standard_Error, ...)` | `std::cerr` |
| `Get_Line` over a file | `std::getline(ifstream, line)` |
| `Integer'Image (N)` | **trap**: Ada prefixes non-negative numbers with a blank. `std::to_string` does not. Whichever the reference prints is what parity requires. |
| `Ada.Strings.Fixed.Trim` | hand-written trim helper |
| `X & Y` string concatenation | `x + y` |

## Concurrency (not exercised by this workshop's sample)

| Ada | C++ |
| --- | --- |
| `task` | `std::thread` / `std::jthread` |
| `protected object` | class with a `std::mutex` guarding its state |
| entry with a barrier | `std::condition_variable` |
| `delay Until` | `std::this_thread::sleep_until` |

Concurrency changes observable ordering. If the Ada program's output depends
on task scheduling, the golden-output technique needs a deterministic harness
first — flag it before translating.
