# Tools

- `compare.c` — `compare <file1> <file2> <tolerance>`: element-wise comparison of two result files.
- `benchmark.sh` — `tools/benchmark.sh [input] [output.csv]`: runs every solver in `build/` and writes `solver,N,seconds` rows.
- `plot_times.py` — `plot_times.py a.csv [b.csv ...] -o plot.png`: grouped bar chart of running times per matrix size; with several CSVs the series are prefixed by file name.
