cmake_minimum_required(VERSION 3.16)
project(telemetry_cpp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(PARITY_WERROR "Treat warnings as errors" OFF)

if (MSVC)
  add_compile_options(/W4)
  if (PARITY_WERROR)
    add_compile_options(/WX)
  endif()
else()
  add_compile_options(-Wall -Wextra)
  if (PARITY_WERROR)
    add_compile_options(-Werror)
  endif()
endif()

# Add the translated units here as the migration progresses.
add_executable(telemetry_main
  src/main.cpp
)
target_include_directories(telemetry_main PRIVATE include)

enable_testing()
add_subdirectory(tests)
