#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#define DEBUG 0

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_symbol_random_src.h>

#include <iostream>


#include <boost/random.hpp>
#include <boost/random/uniform_smallint.hpp>
#include <boost/random/variate_generator.hpp>

#include <ofdmi_shared_generator.h>

typedef boost::mt19937 base_generator_type;
typedef boost::shared_ptr<base_generator_type> base_generator_sptr;
  
typedef boost::uniform_smallint<int> distribution_type;
typedef boost::variate_generator<base_generator_type&, distribution_type> rng_type;
typedef boost::shared_ptr<rng_type> rng_sptr;


class ofdm_symbol_random_src::rng_detail
{

  distribution_type dist;
  base_generator_sptr generator;
  rng_sptr rng;
  
public:
  
  rng_detail( int max ) 
    : dist( 0, max ),
      generator( new base_generator_type() ),
      rng( new rng_type( *generator, dist ) )
  {
    generator->seed( *get_shared_generator() );
    
    volatile rng_type::result_type f;
    for( int i = 0; i < 1000000; ++i ){
      f = (*rng)();
    }
  }
  
  rng_type::result_type
  get_sample( void )
  {
    return (*rng)();
  }
  
};

ofdm_symbol_random_src_sptr 
ofdm_make_symbol_random_src(
    const std::vector<gr_complex>& symbols, int vlen )
{
  return ofdm_symbol_random_src_sptr( new ofdm_symbol_random_src( symbols, 
      vlen ) );
}

ofdm_symbol_random_src::ofdm_symbol_random_src( 
    const std::vector<gr_complex>& symbols, int vlen )

  : gr_sync_block( "symbol_random_src", 
           gr_make_io_signature ( 0, 0, 0 ),
           gr_make_io_signature2( 1, 2, sizeof(gr_complex)*vlen,
                                        sizeof(char)*vlen ) ),
           
  d_symbols( symbols ), 
  d_vlen( vlen ),
  d_rng_detail( new rng_detail( symbols.size()-1 ) )
  
{
}

int 
ofdm_symbol_random_src::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  gr_complex *out = static_cast<gr_complex*>( output_items[0] );
  char *ind_out = 0;
  
  if( output_items.size() > 1 ){
    ind_out = static_cast<char*>( output_items[1] );
  }
  
  for( int i = 0; i < noutput_items * d_vlen; ++i ) {
    
    const rng_type::result_type ind = d_rng_detail->get_sample();
    
    out[i] = d_symbols[ ind ];
    
    if ( ind_out != 0 ) {
      ind_out[i] = static_cast<char>( ind );
    }
    
  }
  
  if( DEBUG ) {
    std::cout << "[sym rand src " << unique_id() << "] produced " 
              << noutput_items << " items" << std::endl;
  }
  
  return noutput_items;
}
