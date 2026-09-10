#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "telemetry/alerts.hpp"
#include "telemetry/parsing.hpp"
#include "telemetry/sensors.hpp"
#include "telemetry/stats.hpp"
#include "telemetry/telemetry.hpp"

namespace {

using namespace telemetry;

constexpr int kMaxReadings = 256;

sensors::SensorTable make_table() {
  sensors::SensorTable table;
  table.push_back(std::make_unique<sensors::Thermocouple>(
      7, "boiler-inlet", Celsius::from_tenths(15)));
  table.push_back(std::make_unique<sensors::Thermistor>(
      12, "cabin-air", Celsius::from_tenths(200)));
  table.push_back(std::make_unique<sensors::Thermocouple>(
      31, "exhaust", Celsius::from_tenths(-20)));
  return table;
}

std::vector<alerts::Rule> make_rules() {
  return {
      alerts::Rule{7, alerts::Above{Celsius::from_tenths(900)}},
      alerts::Rule{12, alerts::Below{Celsius::from_tenths(180)}},
      alerts::Rule{31, alerts::Stuck{3}},
  };
}

std::vector<Reading> load(const std::string& path) {
  std::ifstream file(path);
  if (!file) {
    throw InvalidReading("cannot open " + path);
  }

  std::vector<Reading> data;
  std::string line;
  while (std::getline(file, line)) {
    if (parsing::is_skippable(line)) {
      continue;
    }
    if (static_cast<int>(data.size()) == kMaxReadings) {
      throw InvalidReading("too many readings");
    }
    data.push_back(parsing::parse_line(line));
  }
  return data;
}

void report(const std::vector<Reading>& data) {
  const sensors::SensorTable table = make_table();

  std::vector<Reading> calibrated;
  calibrated.reserve(data.size());
  for (const Reading& item : data) {
    const sensors::Sensor& sensor = sensors::find(table, item.id);
    calibrated.push_back(Reading{item.id, item.time,
                                 sensor.calibrate(item.value), item.state});
  }

  std::cout << "TELEMETRY REPORT\n";
  std::cout << "================\n";
  std::cout << "readings: " << image(static_cast<int>(data.size())) << "\n";

  std::cout << "\n";
  std::cout << "sensors:\n";
  for (const auto& sensor : table) {
    std::cout << "  " << sensor->describe() << "\n";
  }

  std::cout << "\n";
  std::cout << "calibrated summary (good readings only):\n";
  const stats::Summary summary = stats::summarise(calibrated);
  std::cout << "  count: " << image(summary.count) << "\n";
  std::cout << "  min:   " << image(summary.minimum) << "\n";
  std::cout << "  max:   " << image(summary.maximum) << "\n";
  std::cout << "  mean:  " << image(summary.mean) << "\n";
  std::cout << "  suspect readings: "
            << image(stats::count_where(calibrated, [](const Reading& item) {
                 return item.state == Quality::Suspect;
               }))
            << "\n";

  std::cout << "\n";
  std::cout << "alerts:\n";
  const std::vector<alerts::Alert> found =
      alerts::evaluate(calibrated, make_rules());
  if (found.empty()) {
    std::cout << "  none\n";
  } else {
    for (const alerts::Alert& alert : found) {
      std::cout << "  t=" << image(alert.time) << " sensor "
                << image(alert.id) << ": " << alert.message << "\n";
    }
  }
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: telemetry_main <readings-file>\n";
    return 2;
  }

  try {
    report(load(argv[1]));
  } catch (const InvalidReading& error) {
    std::cerr << "rejected: " << error.what() << "\n";
    return 2;
  } catch (const std::exception&) {
    std::cerr << "failed: " << "unexpected error" << "\n";
    return 2;
  }

  return 0;
}
