#!/usr/bin/env bash
# Runs every available solver on an input file and writes a CSV (solver,N,seconds).
# Usage: tools/benchmark.sh [input_file] [output_csv]
set -euo pipefail

cd "$(dirname "$0")/.."
INPUT="${1:-input/input}"
OUT="${2:-results/times.csv}"

mkdir -p "$(dirname "$OUT")"
echo "solver,N,seconds" > "$OUT"

for bin in build/solver_*; do
	[ -x "$bin" ] || continue
	name="${bin#build/solver_}"
	"$bin" "$INPUT" | sed -n "s/.*N=\([0-9]*\): Time=\([0-9.]*\).*/$name,\1,\2/p" >> "$OUT"
done
rm -f out[0-9]*
echo "Wrote $OUT"
