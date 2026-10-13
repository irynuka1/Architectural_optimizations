CC      := gcc
CFLAGS  := -Wall -Werror -O0 -march=native -Iinclude
BUILD   := build

SOLVERS := neopt opt opt_zen2 blas
BINS    := $(addprefix $(BUILD)/solver_,$(SOLVERS)) $(BUILD)/compare

all: $(BINS)

$(BUILD):
	mkdir -p $@

$(BUILD)/solver_blas: src/solvers/solver_blas.c src/main.c include/utils.h | $(BUILD)
	$(CC) $(CFLAGS) src/solvers/solver_blas.c src/main.c -lopenblas -o $@

$(BUILD)/solver_%: src/solvers/solver_%.c src/main.c include/utils.h | $(BUILD)
	$(CC) $(CFLAGS) src/solvers/solver_$*.c src/main.c -o $@

$(BUILD)/compare: tools/compare.c include/utils.h | $(BUILD)
	$(CC) $(CFLAGS) tools/compare.c -lm -o $@

clean:
	rm -rf $(BUILD) out*

.PHONY: all clean
