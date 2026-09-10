#include "telemetry/stats.hpp"

namespace telemetry::stats {

Summary summarise(const std::vector<Reading>& data) {
  int count = 0;
  int total = 0;
  Celsius low = Celsius::from_tenths(Celsius::kMaxTenths);
  Celsius high = Celsius::from_tenths(Celsius::kMinTenths);

  for (const Reading& item : data) {
    if (item.state != Quality::Good) {
      continue;
    }
    ++count;
    total += item.value.tenths();
    if (item.value < low) low = item.value;
    if (item.value > high) high = item.value;
  }

  if (count == 0) {
    throw InvalidReading("no good readings to summarise");
  }

  return Summary{count, low, high, Celsius::from_tenths(total / count)};
}

}  // namespace telemetry::stats
