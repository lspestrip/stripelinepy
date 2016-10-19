/******************************************************************************
 * flatrng.c
 *
 * Implementation of a "xorshift" uniform random number generator, as
 * described in the paper
 *
 * "Xorshift RNGs", Marsaglia G., Journal of Statistical Software,
 * 8(14), 2003 (DOI 10.18637/jss.v008.i14)
 *
 * The code here uses four 32-bit integers, so that the period is
 * 2^128-1. The default initial seeds has been chosen in order to
 * match the ones used in the software package "absrand" 1.1, by
 * Plaszczynski
 * (http://planck.lal.in2p3.fr/wiki/pmwiki.php/Softs/AbsRand).
 *
 ******************************************************************************
 *
 * IMPLEMENTATION NOTES
 *
 * The "state" of the RNG is described by four 32-bit integer numbers.
 * In order to agree with the results of Plaszczynski's code, the
 * internal implementation of the routines use unsigned integers.
 * (This is the reason why this code has not have been ported to
 * Fortran, by the way, as standard Fortran does not allow unsigned
 * integer types.)
 *
 * The "oof2" (1/f^2) RNG has an internal state of 5 double numbers.
 * It uses Plaszczynski's algorith.
 *
 * The code has been written with the aim of being wrapped
 * automatically using "f2py" (which, despite its name, is able to
 * wrap C functions too).
 *
 ******************************************************************************/

#include <math.h>
#include <stdint.h>

const double PI = 3.14159265358979323846;
const double scale_factor = 1.0 / (1.0 + (double)0xFFFFFFFF);

/******************************************************************************/

static void twiddle(uint32_t *v) {
  int i;
  for (i = 0; i < 9; ++i) {
    *v ^= *v << 13;
    *v ^= *v >> 17;
    *v ^= *v << 5;
  }
}

/******************************************************************************/

/* Make the RNG advance its state by one step */
#define NEXT_STATE(ustate)                                                     \
  {                                                                            \
    uint32_t tmp = ustate[0] ^ (ustate[0] << 11);                              \
    ustate[0] = ustate[1];                                                     \
    ustate[1] = ustate[2];                                                     \
    ustate[2] = ustate[3];                                                     \
    ustate[3] = (ustate[3] ^ (ustate[3] >> 19)) ^ (tmp ^ (tmp >> 8));          \
  }

/******************************************************************************/

/* Return a random number with uniform distribution in the full range
 * of the int32_t datatype */
static uint32_t int_rand_uni(int32_t *state) {
  uint32_t *ustate = (uint32_t *)state;
  NEXT_STATE(ustate);
  return ustate[3];
}

/******************************************************************************/

void init_rng(int32_t x_start, int32_t y_start, int32_t z_start,
              int32_t w_start, int32_t *state) {
  uint32_t *ustate = (uint32_t *)state;
  int i;

  state[0] = x_start != 0 ? x_start : 123456789;
  state[1] = y_start != 0 ? y_start : 362436069;
  state[2] = z_start != 0 ? z_start : 521288629;
  state[3] = w_start != 0 ? w_start : 88675123;
  state[4] = 1;

  /* Shuffle the bits of the seeds */
  twiddle(&ustate[0]);
  twiddle(&ustate[1]);
  twiddle(&ustate[2]);
  twiddle(&ustate[3]);

  /* Burn in the RNG */
  for (i = 0; i < 16; ++i) {
    NEXT_STATE(ustate);
  }
}

/******************************************************************************/

/* Return a random uniform number in the interval [0, 1[ */
double rand_uniform(int32_t *state) {
  return int_rand_uni(state) * scale_factor;
}

/******************************************************************************/

/* Fill a vector with random uniform numbers */
void fill_vector_uniform(int32_t *state, double *array, int num) {
  uint32_t *ustate = (uint32_t *)state;
  int i;

  for (i = 0; i < num; ++i) {
    NEXT_STATE(ustate);
    array[i] = ustate[3] * scale_factor;
  }
}

/******************************************************************************/

double rand_normal(int32_t *state, int8_t *empty, double *gset) {
  if (*empty) {
    double v1, v2, rsq;
    double fac;
    do {
      v1 = 2.0 * rand_uniform(state) - 1.0;
      v2 = 2.0 * rand_uniform(state) - 1.0;
      rsq = v1 * v1 + v2 * v2;
    } while ((rsq >= 1) || (rsq == 0));

    fac = sqrt(-2.0 * log(rsq) / rsq);
    *gset = v1 * fac;
    *empty = 0;
    return v2 * fac;
  } else {
    *empty = 1;
    return *gset;
  }
}

/******************************************************************************/

void fill_vector_normal(int32_t *state, int8_t *empty, double *gset,
                        double *array, int num) {
  int i;
  for (i = 0; i < num; ++i) {
    array[i] = rand_normal(state, empty, gset);
  }
}

/******************************************************************************/

#define OOF2_C0(state) (state[0])
#define OOF2_C1(state) (state[1])
#define OOF2_D0(state) (state[2])
#define OOF2_X1(state) (state[3])
#define OOF2_Y1(state) (state[4])

void init_oof2(double fmin, double fknee, double fsample, double *oof2_state) {
  double w0 = PI * fmin / fsample;
  double w1 = PI * fknee / fsample;

  OOF2_C0(oof2_state) = (1.0 + w1) / (1.0 + w0);
  OOF2_C1(oof2_state) = -(1.0 - w1) / (1.0 + w0);
  OOF2_D0(oof2_state) = (1.0 - w0) / (1.0 + w0);
  OOF2_X1(oof2_state) = 0;
  OOF2_Y1(oof2_state) = 0;
}

/******************************************************************************/

double rand_oof2(int32_t *flat_state, int8_t *empty, double *gset,
                 double *oof2_state) {
  double x2 = rand_normal(flat_state, empty, gset);
  double y2 = OOF2_C0(oof2_state) * x2 +
              OOF2_C1(oof2_state) * OOF2_X1(oof2_state) +
              OOF2_D0(oof2_state) * OOF2_Y1(oof2_state);
  OOF2_X1(oof2_state) = x2;
  OOF2_Y1(oof2_state) = y2;

  return y2;
}
