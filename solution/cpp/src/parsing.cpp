#include "telemetry/parsing.hpp"

#include <array>
#include <cctype>

namespace telemetry::parsing {
namespace {

std::string trim(const std::string& text) {
  std::size_t first = 0;
  while (first < text.size() &&
         std::isspace(static_cast<unsigned char>(text[first]))) {
    ++first;
  }
  std::size_t last = text.size();
  while (last > first &&
         std::isspace(static_cast<unsigned char>(text[last - 1]))) {
    --last;
  }
  return text.substr(first, last - first);
}

int to_natural(const std::string& text, const std::string& line) {
  if (text.empty()) {
    throw InvalidReading("empty number: " + line);
  }
  int value = 0;
  for (const char digit : text) {
    if (digit < '0' || digit > '9') {
      throw InvalidReading("not a number: " + line);
    }
    value = value * 10 + (digit - '0');
  }
  return value;
}

int to_tenths(const std::string& text, const std::string& line) {
  const bool negative = !text.empty() && text.front() == '-';
  const std::string body = negative ? text.substr(1) : text;
  const std::size_t dot = body.find('.');

  int whole = 0;
  int frac = 0;
  if (dot == std::string::npos) {
    whole = to_natural(body, line);
  } else {
    whole = to_natural(body.substr(0, dot), line);
    if (dot + 2 != body.size()) {
      throw InvalidReading("expected one decimal: " + line);
    }
    frac = to_natural(body.substr(dot + 1), line);
  }
  return (negative ? -1 : 1) * (whole * 10 + frac);
}

Quality to_quality(const std::string& text, const std::string& line) {
  if (text == "G") return Quality::Good;
  if (text == "S") return Quality::Suspect;
  if (text == "B") return Quality::Bad;
  throw InvalidReading("unknown quality: " + line);
}

std::array<std::size_t, 4> field_ends(const std::string& line) {
  std::array<std::size_t, 4> ends{};
  std::size_t found = 0;
  for (std::size_t index = 0; index < line.size(); ++index) {
    if (line[index] == ',') {
      ++found;
      if (found > 3) {
        throw InvalidReading("too many fields: " + line);
      }
      ends[found - 1] = index;
    }
  }
  if (found != 3) {
    throw InvalidReading("expected 4 fields: " + line);
  }
  ends[3] = line.size();
  return ends;
}

std::string field(const std::string& line, std::size_t from, std::size_t to) {
  return trim(line.substr(from, to - from));
}

}  // namespace

Reading parse_line(const std::string& line) {
  const std::array<std::size_t, 4> ends = field_ends(line);

  const int raw_id = to_natural(field(line, 0, ends[0]), line);
  const int raw_time = to_natural(field(line, ends[0] + 1, ends[1]), line);
  const int tenths = to_tenths(field(line, ends[1] + 1, ends[2]), line);
  const Quality state = to_quality(field(line, ends[2] + 1, ends[3]), line);

  if (raw_id < kMinSensorId || raw_id > kMaxSensorId) {
    throw InvalidReading("sensor id out of range: " + line);
  }
  if (raw_time > kMaxTimestamp) {
    throw InvalidReading("timestamp out of range: " + line);
  }
  if (tenths < Celsius::kMinTenths || tenths > Celsius::kMaxTenths) {
    throw InvalidReading("temperature out of range: " + line);
  }

  return Reading{raw_id, raw_time, Celsius::from_tenths(tenths), state};
}

bool is_skippable(const std::string& line) {
  const std::string stripped = trim(line);
  return stripped.empty() || stripped.front() == '#';
}

}  // namespace telemetry::parsing
