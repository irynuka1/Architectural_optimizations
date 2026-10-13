/*
 * ASC Assignment 2
 * 2026 Spring
 */
#include "utils.h"

/*
 * Optimized implementation: loop reordering, pointer increments, registers, unrolling
 */
double* my_solver(int N, double *A, double *B, double *x) {
	double *C = calloc(N * N, sizeof(double));
	double *D = calloc(N * N, sizeof(double));
	double *y = calloc(N, sizeof(double));

	if (!C || !D || !y) {
		free(C); free(D); free(y);
		return NULL;
	}

	/* C = At * B
	 * Loop order k,i,j.
	 * Pointer increments on pC and pB.
	 * Register variables to avoid multiple memory accesses.
	 * The inner loop unrolled by 4.
	 */
	for (int k = 0; k < N; k++) {
		register double *pA_k = A + k * N;
		register double *pB_k = B + k * N;

		for (int i = 0; i < N; i++) {
			register double a_ki = pA_k[i];
			register double *pB = pB_k;
			register double *pC = C + i * N;
			register double *pC_end = pC + N;

			while (pC < pC_end - 4) {
				register double c0 = pC[0];
				register double c1 = pC[1];
				register double c2 = pC[2];
				register double c3 = pC[3];

				c0 += a_ki * pB[0];
				c1 += a_ki * pB[1];
				c2 += a_ki * pB[2];
				c3 += a_ki * pB[3];

				pC[0] = c0;
				pC[1] = c1;
				pC[2] = c2;
				pC[3] = c3;

				pC += 4;
				pB += 4;
			}

			while (pC < pC_end)
    			*pC++ += a_ki * *pB++;
		}
	}

	/* D = C * Ct, D is symmetric
	 * Compute only upper triangle, then mirror.
	 * Loop order i,j,k with pointer increments.
	 * The inner loop unrolled by 4.
	 */
	for (int i = 0; i < N; i++) {
		register double *pCi = C + i * N;
    	register double *pCi_end = pCi + N;
		register double *pCj = C + i * N;

		for (int j = i; j < N; j++) {
			register double *pCi_k = pCi;
			register double *pCj_k = pCj;
			register double s0 = 0.0, s1 = 0.0, s2 = 0.0, s3 = 0.0;

			while (pCi_k <= pCi_end - 4) {
                s0 += pCi_k[0] * pCj_k[0];
				s1 += pCi_k[1] * pCj_k[1];
				s2 += pCi_k[2] * pCj_k[2];
				s3 += pCi_k[3] * pCj_k[3];

				pCi_k += 4;
				pCj_k += 4;
			}

			register double sum = s0 + s1 + s2 + s3;
			while (pCi_k < pCi_end)
    			sum += *pCi_k++ * *pCj_k++;

			D[i * N + j] = sum;
			D[j * N + i] = sum;

			pCj += N;
		}
	}

	/* y = sum(i=0..N-1) D * linie(C, i)
	 * y[r] = sum_k D[r][k] * C[i][k]
	 * Loop order r,i,k: pD_r calculated once per r-iteration.
	 * y accumulator scalar in register to avoid multiple writes to y[r].
	 * The inner loop unrolled by 4.
	 */
	for (int r = 0; r < N; r++) {
		register double y0 = 0.0, y1 = 0.0, y2 = 0.0, y3 = 0.0;
		register double *pD_r = D + r * N;

		for (int i = 0; i < N; i++) {
			register double *pCi = C + i * N;
			register double *pCi_end = pCi + N;
			register double *pD_k = pD_r;

			while (pCi <= pCi_end - 4) {
				y0 += pD_k[0] * pCi[0];
				y1 += pD_k[1] * pCi[1];
				y2 += pD_k[2] * pCi[2];
				y3 += pD_k[3] * pCi[3];

				pD_k += 4;
				pCi += 4;
			}

			while (pCi < pCi_end)
				y0 += *pD_k++ * *pCi++;
		}

		y[r] += y0 + y1 + y2 + y3;
	}

	// y = y + x
	for (int i = 0; i < N; i++)
		y[i] += x[i];

	free(C);
	free(D);

	return y;	
}

