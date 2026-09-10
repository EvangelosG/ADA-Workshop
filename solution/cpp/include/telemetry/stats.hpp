#pragma once

#include <vector>

#include "telemetry/telemetry.hpp"

namespace telemetry::stats {

struct Summary {
  int count = 0;
  Celsius minimum{};
  Celsius maximum{};
  Celsius mean{};
};

// Only Good readings take part. Throws InvalidReading when none qualify.
Summary summarise(const std::vector<Reading>& data);

// Ada generic -> function template.
template <typename Predicate>
int count_where(const std::vector<Reading>& data, Predicate selected) {
  int total = 0;
  for (const Reading& item : data) {
    if (selected(item)) {
      ++total;
    }
  }
  return total;
}

}  // namespace telemetry::stats
