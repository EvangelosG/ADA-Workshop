#pragma once

#include <string>
#include <variant>
#include <vector>

#include "telemetry/telemetry.hpp"

namespace telemetry::alerts {

// Ada discriminated record with a variant part -> std::variant of the
// per-discriminant payloads.
struct Above {
  Celsius threshold{};
};
struct Below {
  Celsius threshold{};
};
struct Stuck {
  int window = 1;
};

struct Rule {
  SensorId id = kMinSensorId;
  std::variant<Above, Below, Stuck> kind;
};

struct Alert {
  SensorId id = kMinSensorId;
  Timestamp time = 0;
  std::string message;
};

// Rule order first, then reading order, exactly as the Ada loops.
std::vector<Alert> evaluate(const std::vector<Reading>& data,
                            const std::vector<Rule>& rules);

}  // namespace telemetry::alerts
