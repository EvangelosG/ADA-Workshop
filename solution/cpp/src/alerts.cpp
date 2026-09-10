#include "telemetry/alerts.hpp"

namespace telemetry::alerts {
namespace {

// The Ada alert message field is String (1 .. 40); longer text is cut off.
constexpr std::size_t kMessageCapacity = 40;

Alert make_alert(SensorId id, Timestamp time, const std::string& message) {
  return Alert{id, time, message.substr(0, std::min(message.size(),
                                                    kMessageCapacity))};
}

bool is_stuck(const std::vector<Reading>& data, std::size_t at_index,
              SensorId id, int window) {
  int seen = 0;
  for (std::size_t index = at_index + 1; index-- > 0;) {
    if (data[index].id != id) {
      continue;
    }
    if (data[index].value != data[at_index].value) {
      return false;
    }
    ++seen;
    if (seen == window) {
      break;
    }
  }
  return seen == window;
}

}  // namespace

std::vector<Alert> evaluate(const std::vector<Reading>& data,
                            const std::vector<Rule>& rules) {
  std::vector<Alert> alerts;

  for (const Rule& rule : rules) {
    for (std::size_t index = 0; index < data.size(); ++index) {
      const Reading& item = data[index];
      if (item.id != rule.id || item.state == Quality::Bad) {
        continue;
      }

      if (const auto* above = std::get_if<Above>(&rule.kind)) {
        if (item.value > above->threshold) {
          alerts.push_back(make_alert(rule.id, item.time,
                                      "above " + image(above->threshold) +
                                          " (" + image(item.value) + ")"));
        }
      } else if (const auto* below = std::get_if<Below>(&rule.kind)) {
        if (item.value < below->threshold) {
          alerts.push_back(make_alert(rule.id, item.time,
                                      "below " + image(below->threshold) +
                                          " (" + image(item.value) + ")"));
        }
      } else if (const auto* stuck = std::get_if<Stuck>(&rule.kind)) {
        if (is_stuck(data, index, rule.id, stuck->window)) {
          alerts.push_back(make_alert(rule.id, item.time,
                                      "stuck at " + image(item.value)));
        }
      }
    }
  }

  return alerts;
}

}  // namespace telemetry::alerts
