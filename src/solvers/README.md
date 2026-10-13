# Solvers

Each file defines `double *my_solver(int N, double *A, double *B, double *x)` computing `y = D · Σᵢ row(C,i) + x` with `C = Aᵀ·B` and `D = C·Cᵀ`.

| File | Description |
| --- | --- |
| `solver_neopt.c` | Baseline, straightforward triple loops. |
| `solver_opt.c` | Loop reordering, pointer increments, registers, 4× unrolling. |
| `solver_opt_zen2.c` | `solver_opt.c` + cache blocking tuned for a 512 KB L2. |
| `solver_blas.c` | OpenBLAS (`cblas.h`, link with `-lopenblas`). |

Build one with `make build/solver_<name>` from the repository root, where `<name>` is `neopt`, `opt`, `opt_zen2` or `blas`.
