#pragma once

#include <cstdlib>
#include <stdexcept>
#include <string>

namespace telemetry {

// Ada's `type Celsius is delta 0.1 digits 6` is exact decimal arithmetic, so
// the C++ counterpart stores tenths of a degree in an integer rather than a
// double. Division truncates towards zero in both languages.
class Celsius {
 public:
  constexpr Celsius() = default;
  static constexpr Celsius from_tenths(int tenths) { return Celsius(tenths); }

  constexpr int tenths() const { return tenths_; }

  constexpr Celsius operator+(Celsius other) const {
    return Celsius(tenths_ + other.tenths_);
  }
  constexpr Celsius operator-(Celsius other) const {
    return Celsius(tenths_ - other.tenths_);
  }
  constexpr Celsius halved() const { return Celsius(tenths_ / 2); }

  constexpr bool operator<(Celsius other) const {
    return tenths_ < other.tenths_;
  }
  constexpr bool operator>(Celsius other) const {
    return tenths_ > other.tenths_;
  }
  constexpr bool operator==(Celsius other) const {
    return tenths_ == other.tenths_;
  }
  constexpr bool operator!=(Celsius other) const {
    return tenths_ != other.tenths_;
  }

  static constexpr int kMinTenths = -800;
  static constexpr int kMaxTenths = 1500;

 private:
  explicit constexpr Celsius(int tenths) : tenths_(tenths) {}
  int tenths_ = 0;
};

using SensorId = int;
using Timestamp = int;

constexpr SensorId kMinSensorId = 1;
constexpr SensorId kMaxSensorId = 99;
constexpr Timestamp kMaxTimestamp = 86399;

enum class Quality { Good, Suspect, Bad };

struct Reading {
  SensorId id = kMinSensorId;
  Timestamp time = 0;
  Celsius value{};
  Quality state = Quality::Good;
};

// Mirrors Ada's Invalid_Reading exception; the message is part of the
// program's observable behaviour.
class InvalidReading : public std::runtime_error {
 public:
  explicit InvalidReading(const std::string& message)
      : std::runtime_error(message) {}
};

std::string image(Celsius value);
std::string image(int value);

}  // namespace telemetry
