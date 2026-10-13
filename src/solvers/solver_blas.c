/*
 * ASC Assignment 2
 * 2026 Spring
 */
#include "utils.h"
#include <cblas.h>

/*
 * BLAS implementation (OpenBLAS)
 */
double* my_solver(int N, double *A, double *B, double *x) {
	double *C    = calloc(N * N, sizeof(double));
	double *D    = calloc(N * N, sizeof(double));
	double *t    = calloc(N, sizeof(double));
	double *ones = calloc(N, sizeof(double));
	double *y    = calloc(N, sizeof(double));

	if (!C || !D || !t || !ones || !y) {
		free(C); free(D); free(t); free(ones); free(y);
		return NULL;
	}

	for (int i = 0; i < N; i++)
		ones[i] = 1.0;

	// C = At * B
	cblas_dgemm(CblasRowMajor, CblasTrans, CblasNoTrans, N, N, N, 1.0, A, N, B, N, 0.0, C, N);

	// D = C * Ct, D is symmetric so dsyrk for the upper triangle
	cblas_dsyrk(CblasRowMajor, CblasUpper, CblasNoTrans, N, N, 1.0, C, N, 0.0, D, N);

	// t[k] = sum of column k of C = Ct * ones
	cblas_dgemv(CblasRowMajor, CblasTrans, N, N, 1.0, C, N, ones, 1, 0.0, t, 1);

	// y = D * t, D is symmetric so dsymv for the upper triangle
	cblas_dsymv(CblasRowMajor, CblasUpper, N, 1.0, D, N, t, 1, 0.0, y, 1);

	// y = y + x
	cblas_daxpy(N, 1.0, x, 1, y, 1);

	free(C);
	free(D);
	free(t);
	free(ones);

	return y;
}
