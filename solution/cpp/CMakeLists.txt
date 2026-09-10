cmake_minimum_required(VERSION 3.16)
project(telemetry_cpp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (MSVC)
  add_compile_options(/W4)
else()
  add_compile_options(-Wall -Wextra)
endif()

add_executable(telemetry_main
  src/main.cpp
  src/telemetry.cpp
  src/sensors.cpp
  src/parsing.cpp
  src/stats.cpp
  src/alerts.cpp
)
target_include_directories(telemetry_main PRIVATE include)

enable_testing()
add_subdirectory(tests)
