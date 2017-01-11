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
#include <stdlib.h>

const double PI = 3.14159265358979323846;
const double scale_factor = 1.0 / (1.0 + (double)0xFFFFFFFF);

/******************************************************************************/

static void twiddle(uint32_t *v)
{
  int i;
  for (i = 0; i < 9; ++i)
  {
    *v ^= *v << 13;
    *v ^= *v >> 17;
    *v ^= *v << 5;
  }
}

/******************************************************************************/

/* Make the RNG advance its state by one step */
#define NEXT_STATE(ustate)                                            \
  {                                                                   \
    uint32_t tmp = ustate[0] ^ (ustate[0] << 11);                     \
    ustate[0] = ustate[1];                                            \
    ustate[1] = ustate[2];                                            \
    ustate[2] = ustate[3];                                            \
    ustate[3] = (ustate[3] ^ (ustate[3] >> 19)) ^ (tmp ^ (tmp >> 8)); \
  }

/******************************************************************************/

/* Return a random number with uniform distribution in the full range
 * of the int32_t datatype */
static uint32_t int_rand_uni(int32_t *state)
{
  uint32_t *ustate = (uint32_t *)state;
  NEXT_STATE(ustate);
  return ustate[3];
}

/******************************************************************************/

void init_rng(int32_t x_start, int32_t y_start, int32_t z_start,
              int32_t w_start, int32_t *state)
{
  uint32_t *ustate = (uint32_t *)state;
  int i;

  state[0] = x_start != 0 ? x_start : 123456789;
  state[1] = y_start != 0 ? y_start : 362436069;
  state[2] = z_start != 0 ? z_start : 521288629;
  state[3] = w_start != 0 ? w_start : 88675123;

  /* Shuffle the bits of the seeds */
  twiddle(&ustate[0]);
  twiddle(&ustate[1]);
  twiddle(&ustate[2]);
  twiddle(&ustate[3]);

  /* Burn in the RNG */
  for (i = 0; i < 16; ++i)
  {
    NEXT_STATE(ustate);
  }
}

/******************************************************************************/

/* Return a random uniform number in the interval [0, 1[ */
double rand_uniform(int32_t *state)
{
  return int_rand_uni(state) * scale_factor;
}

/******************************************************************************/

/* Fill a vector with random uniform numbers */
void fill_vector_uniform(int32_t *state, double *array, int num)
{
  uint32_t *ustate = (uint32_t *)state;
  int i;

  for (i = 0; i < num; ++i)
  {
    NEXT_STATE(ustate);
    array[i] = ustate[3] * scale_factor;
  }
}

/******************************************************************************/

double rand_normal(int32_t *state, int8_t *empty, double *gset)
{
  if (*empty)
  {
    double v1, v2, rsq;
    double fac;
    do
    {
      v1 = 2.0 * rand_uniform(state) - 1.0;
      v2 = 2.0 * rand_uniform(state) - 1.0;
      rsq = v1 * v1 + v2 * v2;
    } while ((rsq >= 1) || (rsq == 0));

    fac = sqrt(-2.0 * log(rsq) / rsq);
    *gset = v1 * fac;
    *empty = 0;
    return v2 * fac;
  }
  else
  {
    *empty = 1;
    return *gset;
  }
}

/******************************************************************************/

void fill_vector_normal(int32_t *state, int8_t *empty, double *gset,
                        double *array, int num)
{
  int i;
  for (i = 0; i < num; ++i)
  {
    array[i] = rand_normal(state, empty, gset);
  }
}

/******************************************************************************/

int32_t oof2_state_size(void)
{
  return 5;
}

/******************************************************************************/

#define OOF2_C0(state) (state[0])
#define OOF2_C1(state) (state[1])
#define OOF2_D0(state) (state[2])
#define OOF2_X1(state) (state[3])
#define OOF2_Y1(state) (state[4])

void init_oof2(double fmin, double fknee, double fsample, double *oof2_state)
{
  double w0 = PI * fmin / fsample;
  double w1 = PI * fknee / fsample;

  OOF2_C0(oof2_state) = (1.0 + w1) / (1.0 + w0);
  OOF2_C1(oof2_state) = -(1.0 - w1) / (1.0 + w0);
  OOF2_D0(oof2_state) = (1.0 - w0) / (1.0 + w0);
  OOF2_X1(oof2_state) = 0;
  OOF2_Y1(oof2_state) = 0;
}

/******************************************************************************/

double oof2_filter(double *oof2_state, double x2)
{
  const double y2 = OOF2_C0(oof2_state) * x2 +
                    OOF2_C1(oof2_state) * OOF2_X1(oof2_state) +
                    OOF2_D0(oof2_state) * OOF2_Y1(oof2_state);
  OOF2_X1(oof2_state) = x2;
  OOF2_Y1(oof2_state) = y2;

  return y2;
}

/******************************************************************************/

double rand_oof2(int32_t *flat_state, int8_t *empty, double *gset,
                 double *oof2_state)
{
  const double x2 = rand_normal(flat_state, empty, gset);
  return oof2_filter(oof2_state, x2);
}

/******************************************************************************/

void fill_vector_oof2(int32_t *flat_state, int8_t *empty, double *gset,
                      double *oof2_state, double *array, int num)
{
  int i;
  for (i = 0; i < num; ++i)
  {
    array[i] = rand_oof2(flat_state, empty, gset, oof2_state);
  }
}

/******************************************************************************/

int32_t num_of_oof_poles(double fmin, double fknee, double fsample)
{
  const double wmin = log10(2 * M_PI * fmin);
  const double wmax = log10(2 * M_PI * fknee);

  return (int32_t)((wmax - wmin) * 2 + log10(fsample));
}

/******************************************************************************/

int32_t oof_state_size(double fmin, double fknee, double fsample)
{
  return oof2_state_size() * num_of_oof_poles(fmin, fknee, fsample);
}

/******************************************************************************/

int32_t init_oof(double slope, double fmin, double fknee, double fsample,
                 double *oof_state)
{
  const double wmin = log10(2 * M_PI * fmin);
  const double wmax = log10(2 * M_PI * fknee);
  const double a = -slope;
  const int32_t nproc = num_of_oof_poles(fmin, fknee, fsample);
  const double dp = (wmax - wmin) / nproc;

  int32_t i;
  double p = wmin + 0.5 * (1 - 0.5 * a) * dp;
  double z = p + 0.5 * a * dp;

  for (i = 0; i < nproc; ++i)
  {
    init_oof2(pow(10, p) / (2 * M_PI),
              pow(10, z) / (2 * M_PI),
              fsample,
              oof_state + i * oof2_state_size());

    p += dp;
    z = p + 0.5 * a * dp;
  }

  return nproc;
}

/******************************************************************************/

double rand_oof(int32_t *flat_state, int8_t *empty, double *gset,
                double *oof_state, int32_t oof_state_size)
{
  double x2 = rand_normal(flat_state, empty, gset);
  int32_t i;
  for (i = 0; i < oof_state_size; ++i)
  {
    x2 = oof2_filter(oof_state + i * oof2_state_size(), x2);
  }

  return x2;
}

/******************************************************************************/

void fill_vector_oof(int32_t *flat_state, int8_t *empty, double *gset,
                     double *oof_state, int32_t oof_state_size,
                     double *array, int num)
{
  int i;
  for (i = 0; i < num; ++i)
  {
    array[i] = rand_oof(flat_state, empty, gset, oof_state, oof_state_size);
  }
}
