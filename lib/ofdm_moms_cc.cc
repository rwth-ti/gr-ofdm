
/* $Id$ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_moms_cc.h>

#include <iostream>

#define DEBUG 0


ofdm_moms_cc ::
ofdm_moms_cc( double ip_num, double ip_denom )
  : gr_block(
      "moms_cc",
      gr_make_io_signature( 
        1, 1,
        sizeof( gr_complex ) ),
      gr_make_io_signature( 
        1, 1,
        sizeof( gr_complex ) ) )

  , d_ip_num( ip_num )
  , d_ip_denom( ip_denom )
  , d_offset_num( 0 )

{
}


void
ofdm_moms_cc :: 
forecast( 
  int             noutput_items, 
  gr_vector_int & ninput_items_required )
{
  ninput_items_required[0] = ceil(noutput_items*d_ip_num / d_ip_denom) + 3;

  if(ninput_items_required[0] < 4)
  {
    ninput_items_required[0] = 4;
  }
}


int
ofdm_moms_cc :: 
general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

  int ninput = static_cast<int>(ninput_items[0]);

  // Local Variables
  double num = d_offset_num;
  double const denom = d_ip_denom;
  double const ip_num = d_ip_num;

  gr_complex tmp = 0.0;
  int i = 0;

  if(DEBUG) std::cout << "MOMS_FF gen_work: nin: " << ninput << " nout: " << noutput_items << std::endl;

  int j = 0;
  for(j=0;j<noutput_items && i<ninput-3;++j)
  {

    // Calculate values (Farrow Structure)
    float const d = num/denom;
    tmp =         in[i+3]*gr_complex(1./6,0) - in[i+2]*gr_complex(1./2,0) + in[i+1]*gr_complex(1./2,0) - in[i]*gr_complex(1./6,0);
    tmp = d*tmp - in[i+3]*gr_complex(1./6,0) + in[i+2]                    - in[i+1]*gr_complex(3./2,0) + in[i]*gr_complex(2./3,0);
    tmp = d*tmp                              + in[i+2]*gr_complex(1./6,0) + in[i+1]*gr_complex(2./3,0) - in[i]*gr_complex(5./6,0);
    out[j] = d*tmp                                                        + in[i+1]*gr_complex(2./3,0) + in[i]*gr_complex(1/.3,0);

    // Calculate new offset
    num += ip_num;

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


ofdm_moms_cc_sptr
ofdm_make_moms_cc( double ip_num, double ip_denom )
{
  return ofdm_moms_cc::create( ip_num, ip_denom );
}


ofdm_moms_cc_sptr
ofdm_moms_cc ::
create( double ip_num, double ip_denom )
{
  try 
  {
    ofdm_moms_cc_sptr tmp( 
      new ofdm_moms_cc( ip_num, ip_denom ) );

    return tmp;
  } 
  catch ( ... ) 
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_moms_cc" << std::endl;
    throw;
  } // catch ( ... )
}




// GET / SET
void
ofdm_moms_cc ::
set_init_ip_fraction(double num, double denom)
{
  set_ip_fraction(num, denom);
  d_offset_num -= num;
}
void
ofdm_moms_cc ::
set_ip_fraction(double num,double denom)
{
  // Correct the offset numerator
  d_offset_num = d_offset_num*denom/d_ip_denom;

  d_ip_num = num;
  d_ip_denom = denom;
}
double
ofdm_moms_cc ::
get_ip_fraction_num()
{
  return d_ip_num;
}
double
ofdm_moms_cc ::
get_ip_fraction_denom()
{
  return d_ip_denom;
}

void
ofdm_moms_cc ::
set_offset_num(double num)
{
  d_offset_num = num;

}
double
ofdm_moms_cc ::
get_offset_num()
{
  return d_offset_num;
}
