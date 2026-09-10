#pragma once

#include <memory>
#include <string>
#include <vector>

#include "telemetry/telemetry.hpp"

namespace telemetry::sensors {

// Ada tagged type with a dispatching primitive -> abstract base class with
// virtual member functions.
class Sensor {
 public:
  Sensor(SensorId id, std::string label)
      : id_(id), label_(std::move(label)) {}
  virtual ~Sensor() = default;

  SensorId id() const { return id_; }
  const std::string& label() const { return label_; }

  virtual std::string kind() const = 0;
  virtual Celsius calibrate(Celsius raw) const { return raw; }

  std::string describe() const;

 private:
  SensorId id_;
  std::string label_;
};

class Thermocouple : public Sensor {
 public:
  Thermocouple(SensorId id, std::string label, Celsius offset)
      : Sensor(id, std::move(label)), offset_(offset) {}

  std::string kind() const override { return "thermocouple"; }
  Celsius calibrate(Celsius raw) const override { return raw + offset_; }

 private:
  Celsius offset_;
};

class Thermistor : public Sensor {
 public:
  Thermistor(SensorId id, std::string label, Celsius reference)
      : Sensor(id, std::move(label)), reference_(reference) {}

  std::string kind() const override { return "thermistor"; }
  Celsius calibrate(Celsius raw) const override {
    return reference_ + (raw - reference_).halved();
  }

 private:
  Celsius reference_;
};

using SensorTable = std::vector<std::unique_ptr<Sensor>>;

// Throws InvalidReading when no sensor with that id is registered.
const Sensor& find(const SensorTable& table, SensorId id);

}  // namespace telemetry::sensors
