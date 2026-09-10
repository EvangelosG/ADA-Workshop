set(GOLDEN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../golden")
set(DATA_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../ada/data")

function(add_parity_test case_name)
  add_test(NAME parity_${case_name}
    COMMAND ${CMAKE_COMMAND}
      -DEXE=$<TARGET_FILE:telemetry_main>
      -DGOLDEN=${GOLDEN_DIR}
      -DCASE=${case_name}
      -DARGS=${ARGN}
      -P ${CMAKE_CURRENT_SOURCE_DIR}/parity.cmake)
endfunction()

add_parity_test(report "${DATA_DIR}/readings.csv")
add_parity_test(bad_input "${DATA_DIR}/readings_bad.csv")
add_parity_test(calibration_overflow "${DATA_DIR}/readings_overflow.csv")
add_parity_test(missing_file "${DATA_DIR}/no_such_file.csv")
add_parity_test(no_args "")
