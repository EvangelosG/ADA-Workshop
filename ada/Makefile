# Build artefacts land outside ada/ so that verifying the reference build
# never writes into the read-only parts of the tree.
BUILD ?= $(CURDIR)/../.ref-build
BIN   := $(BUILD)/telemetry_main

GOLDEN := $(CURDIR)/../golden
# calibration_overflow and missing_file cover failures that happen *after*
# input validation: a subtype check on a computed value, and an Ada run-time
# exception that is not Invalid_Reading. Both are observable on stderr.
CASES  := report:data/readings.csv bad_input:data/readings_bad.csv \
          calibration_overflow:data/readings_overflow.csv \
          missing_file:data/no_such_file.csv no_args:

.PHONY: all run check-golden golden clean

all: $(BIN)

$(BIN): $(wildcard src/*.ads src/*.adb)
	@mkdir -p $(BUILD)
	gnatmake -q -Isrc -D $(BUILD) -o $(BIN) src/telemetry_main.adb

run: $(BIN)
	$(BIN) data/readings.csv

# Confirms the committed reference outputs still describe the reference
# program, without modifying them. This is the check a migration runs; it
# writes only to $(BUILD).
check-golden: $(BIN)
	@out=$(BUILD)/golden-check; rm -rf $$out; mkdir -p $$out; \
	for spec in $(CASES); do \
	  case_name=$${spec%%:*}; arg=$${spec#*:}; \
	  $(BIN) $$arg > $$out/$$case_name.stdout 2> $$out/$$case_name.stderr; \
	  echo $$? > $$out/$$case_name.exit; \
	  for stream in stdout stderr exit; do \
	    diff -u $(GOLDEN)/$$case_name.$$stream $$out/$$case_name.$$stream \
	      || exit 1; \
	  done; \
	done; \
	echo "golden/ matches the reference program"

# Rewrites the committed reference outputs. Maintainer-only: this is correct
# exactly when the Ada sources changed on purpose, and never during a
# migration.
golden: $(BIN)
	@for spec in $(CASES); do \
	  case_name=$${spec%%:*}; arg=$${spec#*:}; \
	  $(BIN) $$arg > $(GOLDEN)/$$case_name.stdout 2> $(GOLDEN)/$$case_name.stderr; \
	  echo $$? > $(GOLDEN)/$$case_name.exit; \
	done

clean:
	rm -rf $(BUILD)
