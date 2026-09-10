#pragma once

#include <string>

#include "telemetry/telemetry.hpp"

namespace telemetry::parsing {

// Throws InvalidReading with the same message text as the Ada original.
Reading parse_line(const std::string& line);

bool is_skippable(const std::string& line);

}  // namespace telemetry::parsing
