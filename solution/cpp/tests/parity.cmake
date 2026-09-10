# Runs the migrated binary and compares stdout, stderr and the exit status
# against the committed reference outputs.
#
# Required variables (passed with -D):
#   EXE      - path to the C++ executable
#   GOLDEN   - directory holding <CASE>.stdout/.stderr/.exit
#   CASE     - reference case name
#   ARGS     - ';' separated argument list for the executable (may be empty)

if (NOT DEFINED EXE OR NOT DEFINED GOLDEN OR NOT DEFINED CASE)
  message(FATAL_ERROR "parity.cmake requires -DEXE=, -DGOLDEN= and -DCASE=")
endif()

separate_arguments(RUN_ARGS UNIX_COMMAND "${ARGS}")

execute_process(
  COMMAND "${EXE}" ${RUN_ARGS}
  OUTPUT_VARIABLE actual_out
  ERROR_VARIABLE actual_err
  RESULT_VARIABLE actual_status
)

file(READ "${GOLDEN}/${CASE}.stdout" expected_out)
file(READ "${GOLDEN}/${CASE}.stderr" expected_err)
file(READ "${GOLDEN}/${CASE}.exit" expected_status_raw)
string(STRIP "${expected_status_raw}" expected_status)

set(failures "")

if (NOT actual_out STREQUAL expected_out)
  string(APPEND failures
    "\n--- stdout differs ---\nexpected:\n${expected_out}\nactual:\n${actual_out}")
endif()

if (NOT actual_err STREQUAL expected_err)
  string(APPEND failures
    "\n--- stderr differs ---\nexpected:\n${expected_err}\nactual:\n${actual_err}")
endif()

if (NOT actual_status STREQUAL expected_status)
  string(APPEND failures
    "\n--- exit status differs ---\nexpected: ${expected_status}\nactual: ${actual_status}")
endif()

if (NOT failures STREQUAL "")
  message(FATAL_ERROR "parity case '${CASE}' failed:${failures}")
endif()

message(STATUS "parity case '${CASE}' matches the reference output")
