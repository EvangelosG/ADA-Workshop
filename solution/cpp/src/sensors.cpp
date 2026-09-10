#include "telemetry/sensors.hpp"

namespace telemetry::sensors {

std::string Sensor::describe() const {
  return label_ + " [" + kind() + "#" + image(id_) + "]";
}

const Sensor& find(const SensorTable& table, SensorId id) {
  for (const auto& sensor : table) {
    if (sensor && sensor->id() == id) {
      return *sensor;
    }
  }
  throw InvalidReading("unknown sensor id " + image(id));
}

}  // namespace telemetry::sensors
