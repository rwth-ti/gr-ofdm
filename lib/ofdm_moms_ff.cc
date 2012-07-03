
/* $Id: ofdm_moms_ff.cc 1082 2009-07-14 09:57:55Z rohlfing $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>

#include <ofdm_moms_ff.h>

#include <iostream>
#include <math.h>

#define DEBUG 0

ofdm_moms_ff ::
ofdm_moms_ff(  )
  : gr_block(
      "moms_ff",
      gr_make_io_signature(
        1, 1,
        sizeof( float ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( float ) ) )
{
  set_history(2);

  d_ip_num = 0;
  d_ip_denom = 1;

  d_offset_num = 0;

}


void
ofdm_moms_ff ::
forecast(
  int             noutput_items,
  gr_vector_int & ninput_items_required )
{

  ninput_items_required[0] = ceil(noutput_items*d_ip_num / d_ip_denom) + 3;

  if(ninput_items_required[0] < 4)
  {
    ninput_items_required[0] = 4;
  }

  if(DEBUG) std::cout << "MOMS_FF forecast: nout: " << noutput_items << " nin: " << ninput_items_required[0] << std::endl;
}


int
ofdm_moms_ff ::
general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  // Streams
  float const * in = static_cast< float const * >( input_items[0] );
  float * out = static_cast< float * >( output_items[0] );
  int ninput = static_cast<int>(ninput_items[0]);

  // Local Variables
  double num = d_offset_num;
  double denom = d_ip_denom;

  double tmp = 0.0;
  int i = 0;

  if(DEBUG) std::cout << "MOMS_FF gen_work: nin: " << ninput << " nout: " << noutput_items << std::endl;

  int j = 0;
  for(j=0;j<noutput_items && i<ninput-3;++j)
  {

    // Calculate values (Farrow Structure)
    tmp = 0.0;
    tmp = num*tmp/denom + in[i+3]*1/6 - in[i+2]*1/2 + in[i+1]*1/2 - in[i]*1/6;
    tmp = num*tmp/denom - in[i+3]*1/6 + in[i+2]*1/1 - in[i+1]*3/2 + in[i]*2/3;
    tmp = num*tmp/denom               + in[i+2]*1/6 + in[i+1]*2/3 - in[i]*5/6;
    out[j] = num*tmp/denom                          + in[i+1]*2/3 + in[i]*1/3;

    // Calculate new offset
    num += d_ip_num;

    // Handle overflow
    while(num >= denom)
    {
      num -= denom;
      ++i;
    }
  }

  consume_each(i);

  d_offset_num = num;

  return j;
}


// GET / SET
void
ofdm_moms_ff ::
set_init_ip_fraction(double num, double denom)
{
  set_ip_fraction(num, denom);
  d_offset_num -= num;
}
void
ofdm_moms_ff ::
set_ip_fraction(double num,double denom)
{
  // Correct the offset numerator
  d_offset_num = d_offset_num*denom/d_ip_denom;

  d_ip_num = num;
  d_ip_denom = denom;
}
double
ofdm_moms_ff ::
get_ip_fraction_num()
{
  return d_ip_num;
}
double
ofdm_moms_ff ::
get_ip_fraction_denom()
{
  return d_ip_denom;
}

void
ofdm_moms_ff ::
set_offset_num(double num)
{
  d_offset_num = num;

}
double
ofdm_moms_ff ::
get_offset_num()
{
  return d_offset_num;
}




ofdm_moms_ff_sptr
ofdm_make_moms_ff(  )
{
  return ofdm_moms_ff::create(  );
}


ofdm_moms_ff_sptr
ofdm_moms_ff ::
create(  )
{
  try
  {
    ofdm_moms_ff_sptr tmp(
      new ofdm_moms_ff(  ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_moms_ff" << std::endl;
    throw;
  } // catch ( ... )
}
