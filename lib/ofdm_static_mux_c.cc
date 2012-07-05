#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_static_mux_c.h>

#include <iostream>

#define DEBUG 0

ofdm_static_mux_c_sptr 
ofdm_make_static_mux_c( const std::vector<int> &mux_ctrl )
{
  return ofdm_static_mux_c_sptr( new ofdm_static_mux_c( mux_ctrl ) );
}


void 
ofdm_static_mux_c::forecast( int noutput_items, 
    gr_vector_int &ninput_items_required )
{
  assert( d_mux_ctrl[d_mpos] < ninput_items_required.size() );
  
  for(int i = 0; i < ninput_items_required.size(); ++i)
    ninput_items_required[i] = 0;
  
  if( d_mux_ctrl[d_mpos] >= 0 )
    ninput_items_required[ d_mux_ctrl[d_mpos] ] = 1;
  
  // TODO more precise hint
}


ofdm_static_mux_c::ofdm_static_mux_c( const std::vector<int> &mux_ctrl )

  : gr_block("static_mux_c",
           gr_make_io_signature (1, -1, sizeof(gr_complex) ),
           gr_make_io_signature (1,  1, sizeof(gr_complex) ) ),
           
  d_mux_ctrl( mux_ctrl ),
  d_mpos( 0 ),
  d_msize( mux_ctrl.size() )
  
{
  assert( d_msize > 0 );
  
  for( unsigned i = 0; i < mux_ctrl.size(); ++ i ){
    assert( mux_ctrl[i] >= 0 );
  }
  
  if(DEBUG)
    std::cout << "[static mux " << unique_id() << "] msize=" << d_msize
              << std::endl;
}

int 
ofdm_static_mux_c::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  
  if(DEBUG)
    std::cout << "[static mux " << unique_id() << "] entered, state is "
              << "streams=" << input_items.size() 
              << " nout=" << noutput_items;

  
  gr_complex *out = static_cast<gr_complex*>(output_items[0]);
  
  int nout = noutput_items;
  gr_vector_int nin( ninput_items );
  
  
  const gr_complex *in[input_items.size()];
  for( gr_vector_const_void_star::size_type i = 0; 
       i < input_items.size(); 
       ++i )
  {
    in[i] = static_cast<const gr_complex*>(input_items[i]);
    
    if(DEBUG)
      std::cout << " nin[" << i << "]=" << nin[i];
  } // for-loop
  
  
  if(DEBUG)
    std::cout << std::endl;


  int mpos = d_mpos;
  int i;

  for( i = 0; i < nout; ++i ){
    
    const int next_input = d_mux_ctrl[mpos];
    
    if( nin[next_input] > 0 ){
      
      out[i] = *(in[next_input]);
  
      ++in[next_input];
      --nin[next_input];
      
    } else { // nin[next_input] > 0
      
      break;
      
    } // nin[next_input] > 0
        
    ++mpos;
    mpos %= d_msize;
    
  } // for-loop
  
  
  d_mpos = mpos;
    
  
  
  for( unsigned k = 0; k < ninput_items.size(); ++k ){
    consume( k, ninput_items[k] - nin[k] );
  }
  
  
  
  
  if(DEBUG){
    
    std::cout << "[static mux] leave process, d_mpos=" << d_mpos 
              << " produce " << i << " items";
    
    for( unsigned int k = 0; k < nin.size(); ++k ){
      std::cout << " nin[" << k << "]=" << nin[k];
    }
    
    std::cout << std::endl;
    
  } // DEBUG
  
  
  return i;  
}


bool 
ofdm_static_mux_c::check_topology( int ninputs, int noutputs ) 
{ 
  if(DEBUG)
    std::cout << "[static mux " << unique_id() << "] check_topology"
              << " ninputs=" << ninputs << " noutputs=" << noutputs
              << std::endl;
  
  for( int i = 0; i < d_mux_ctrl.size(); ++i ){
    if( d_mux_ctrl[i] < 0 || d_mux_ctrl[i] >= ninputs ){
      
      if(DEBUG)
        std::cout << "[static mux " << unique_id() << "] check topology failed"
                  << std::endl;
    
      return false;
    }
  }
  return true;
}


int 
ofdm_static_mux_c::noutput_forecast( gr_vector_int &ninput_items, 
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{  
  
  int next_input = d_mux_ctrl[d_mpos];
  
  if( next_input >= 0 ){
    assert( next_input < ninput_items.size() );
    
    if( ninput_items[next_input] == 0 && input_done[next_input] ){
      return -1;
    }
    
    if( ninput_items[next_input] == 0 ){
      return 0;
    }
  }
  

  return available_space;  
  
}
