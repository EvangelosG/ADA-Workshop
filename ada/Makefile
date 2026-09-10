BUILD := build
BIN   := $(BUILD)/telemetry_main

.PHONY: all run golden clean

all: $(BIN)

$(BIN): $(wildcard src/*.ads src/*.adb)
	@mkdir -p $(BUILD)
	gnatmake -q -Isrc -D $(BUILD) -o $(BIN) src/telemetry_main.adb

run: $(BIN)
	./$(BIN) data/readings.csv

# Regenerates the committed reference outputs. Only needed if the Ada
# reference implementation changes.
golden: $(BIN)
	./$(BIN) data/readings.csv > ../golden/report.stdout 2> ../golden/report.stderr; \
	  echo $$? > ../golden/report.exit
	./$(BIN) data/readings_bad.csv > ../golden/bad_input.stdout 2> ../golden/bad_input.stderr; \
	  echo $$? > ../golden/bad_input.exit
	./$(BIN) > ../golden/no_args.stdout 2> ../golden/no_args.stderr; \
	  echo $$? > ../golden/no_args.exit

clean:
	rm -rf $(BUILD)
