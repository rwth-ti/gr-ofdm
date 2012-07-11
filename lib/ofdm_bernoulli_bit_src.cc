#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_bernoulli_bit_src.h>

#include <boost/random.hpp>
#include <boost/random/bernoulli_distribution.hpp>
#include <boost/random/variate_generator.hpp>

#include <ofdmi_shared_generator.h>


typedef boost::mt19937 base_generator_type;
typedef boost::shared_ptr<base_generator_type> base_generator_sptr;

typedef boost::bernoulli_distribution<double> distribution_type;
typedef boost::variate_generator<base_generator_type&, distribution_type> rng_type;
typedef boost::shared_ptr<rng_type> rng_sptr;

class ofdm_bernoulli_bit_src::rng_detail
{

  distribution_type dist;
  base_generator_sptr generator;
  rng_sptr rng;
  
public:
  
  rng_detail( double p ) 
    : dist( p ),
      generator( new base_generator_type() ),
      rng( new rng_type( *generator, dist ) )
  {
    generator->seed( *get_shared_generator() );
    
    volatile rng_type::result_type f;
    for( int i = 0; i < 1000000; ++i ){
      f = (*rng)();
    }
  }
  
  void
  gen_bernoulli_sequence( char* out, int N )
  {
    for( int i = 0; i < N; ++i ) {
      out[i] = (*rng)() ? 1 : 0;
    }
  }
};



ofdm_bernoulli_bit_src_sptr 
ofdm_make_bernoulli_bit_src( double p )
{
  return ofdm_bernoulli_bit_src_sptr( new ofdm_bernoulli_bit_src( p ) );
}

ofdm_bernoulli_bit_src::ofdm_bernoulli_bit_src(double p) :
  gr_sync_block(  "bernoulli_bit_src", 
      gr_make_io_signature( 0, 0, sizeof(0) ),
      gr_make_io_signature( 1, 1, sizeof(char)) ),
      
  d_p(p),
  d_rng_detail( new rng_detail( p ) )
  
{
  
}

int 
ofdm_bernoulli_bit_src::work(
  int noutput_items,
  gr_vector_const_void_star &input_items, 
  gr_vector_void_star &output_items )
{
  char *out = static_cast<char*>( output_items[0] );
  
  d_rng_detail->gen_bernoulli_sequence( out, noutput_items );
  
  return noutput_items;
}
