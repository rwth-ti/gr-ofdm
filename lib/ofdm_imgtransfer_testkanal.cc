
/* $Id$ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_imgtransfer_testkanal.h>

#include <iostream>
#include <algorithm>

#define DEBUG 0


ofdm_imgtransfer_testkanal::ofdm_imgtransfer_testkanal(  )
  : gr_block(
      "imgtransfer_testkanal",
      gr_make_io_signature3( 
        3, 3,
        sizeof( unsigned int ),
        sizeof(  char ), sizeof( int) ),
      gr_make_io_signature( 
        1, 1,
        sizeof(  char ) ) )
 ,d_bitcount(0)
 ,d_pos(-1)
 ,d_frameno(0)
 ,d_flag(0)
 ,d_produced(0)
{
}


void
ofdm_imgtransfer_testkanal::forecast( int noutput_items, 
  gr_vector_int &ninput_items_required )
{
}


int
ofdm_imgtransfer_testkanal::general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const unsigned int *in = static_cast< const unsigned int* >( input_items[0] );
  const  char *in_1 = static_cast< const  char* >( input_items[1] );
  const  int *in_2 = static_cast< const  int* >( input_items[2] );
  char *out = static_cast< char* >( output_items[0] );

  if ((ninput_items[0]==0)||(ninput_items[2]==0)) return 0;
  
  if (d_pos==-1)
  {
  	d_bitcount=in[0];
  	d_flag=in_2[0];
  	d_pos=0;
  	d_frameno++;
  }
  
  int ninput;
  if (d_flag==0)
  {
  	ninput = std::min(d_bitcount-d_pos,(unsigned int)std::min(ninput_items[1],noutput_items));
  	std::copy(in_1,in_1+ninput,out);
  	d_pos+=ninput;
  	consume(1,ninput);
  	
  	if (d_pos==d_bitcount)
    {
      consume(0,1);
  	  consume(2,1);
  	  d_pos=-1;
    }
  
    return ninput;
  }
  else
  {
  	int nskip = std::min(d_bitcount-d_pos,(unsigned int)ninput_items[1]);
  	consume(1,nskip);
  	ninput=std::min(d_bitcount-d_produced+d_flag,(unsigned int)noutput_items);
  	d_pos+=nskip;
  	d_produced+=ninput;
  	
    if ((d_pos==d_bitcount)&&(d_produced==(d_bitcount+d_flag)))
    {
   	  consume(0,1);
  	  consume(2,1);
  	  d_pos=-1;
  	  d_produced=0;
    }
  
    return ninput; 	
  }
}


ofdm_imgtransfer_testkanal_sptr
ofdm_make_imgtransfer_testkanal(  )
{
  return ofdm_imgtransfer_testkanal::create(  );
}


ofdm_imgtransfer_testkanal_sptr
ofdm_imgtransfer_testkanal::create(  )
{
  try 
  {
    ofdm_imgtransfer_testkanal_sptr tmp( 
      new ofdm_imgtransfer_testkanal(  ) );

    return tmp;
  } 
  catch ( ... ) 
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_imgtransfer_testkanal" << std::endl;
    throw;
  } // catch ( ... )
}



