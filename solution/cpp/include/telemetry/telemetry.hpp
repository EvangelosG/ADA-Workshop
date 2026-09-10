#pragma once

#include <cstdlib>
#include <stdexcept>
#include <string>

namespace telemetry {

// An Ada run-time exception. The name reaches stderr through the top level
// handler, so it is part of the observable behaviour and is spelled the way
// Ada.Exceptions.Exception_Name spells it.
class AdaError : public std::runtime_error {
 public:
  explicit AdaError(const char* ada_name)
      : std::runtime_error(ada_name), ada_name_(ada_name) {}

  const std::string& ada_name() const { return ada_name_; }

 private:
  std::string ada_name_;
};

class ConstraintError : public AdaError {
 public:
  ConstraintError() : AdaError("CONSTRAINT_ERROR") {}
};

// Raised by Ada.Text_IO.Open when the file does not exist.
class NameError : public AdaError {
 public:
  NameError() : AdaError("ADA.IO_EXCEPTIONS.NAME_ERROR") {}
};

// Ada's `type Celsius is delta 0.1 digits 6 range -80.0 .. 150.0` is exact
// decimal arithmetic, so the C++ counterpart stores tenths of a degree in an
// integer rather than a double. Division truncates towards zero in both
// languages. The range is part of the type: Ada checks it on every value of
// the type, including results of arithmetic, so every construction here goes
// through `checked`.
class Celsius {
 public:
  static constexpr int kMinTenths = -800;
  static constexpr int kMaxTenths = 1500;

  constexpr Celsius() = default;
  static constexpr Celsius from_tenths(int tenths) {
    return Celsius(checked(tenths));
  }

  constexpr int tenths() const { return tenths_; }

  constexpr Celsius operator+(Celsius other) const {
    return from_tenths(tenths_ + other.tenths_);
  }
  constexpr Celsius operator-(Celsius other) const {
    return from_tenths(tenths_ - other.tenths_);
  }
  constexpr Celsius halved() const { return from_tenths(tenths_ / 2); }

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

 private:
  explicit constexpr Celsius(int tenths) : tenths_(tenths) {}

  static constexpr int checked(int tenths) {
    return (tenths < kMinTenths || tenths > kMaxTenths) ? throw ConstraintError()
                                                        : tenths;
  }

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
