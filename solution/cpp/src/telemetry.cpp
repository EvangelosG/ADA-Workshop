#include "telemetry/telemetry.hpp"

namespace telemetry {

std::string image(Celsius value) {
  const int tenths = value.tenths();
  const std::string sign = tenths < 0 ? "-" : "";
  const int magnitude = std::abs(tenths);
  return sign + std::to_string(magnitude / 10) + "." +
         std::to_string(magnitude % 10);
}

std::string image(int value) { return std::to_string(value); }

}  // namespace telemetry
