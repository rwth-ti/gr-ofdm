// @WARNING@

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>

#include "ofdm_puncture_bb.h"
#include <gr_io_signature.h>

#include <string.h>
#include <algorithm>
#include <iostream>

#define DEBUG 0

ofdm_puncture_bb_sptr ofdm_make_puncture_bb (int vlen)
{
	return ofdm_puncture_bb_sptr (new ofdm_puncture_bb (vlen));
}

ofdm_puncture_bb::ofdm_puncture_bb (int vlen)
	: gr_block ("ofdm_puncture_bb",
			   gr_make_io_signature3(3, 3, sizeof(char),            	 // bit stream
					   	   	   	   	   	   sizeof(char)*vlen,            // modemap
										   sizeof(char) ),               // trigger
		       gr_make_io_signature (1, 1, sizeof(char))),
		d_vlen(vlen),
		d_need_bits( 0 ),
		d_out_bits( 0 ),
		d_need_modemap( 1 ),
		d_modemap(new char[vlen]),
		//d_rep_per_mode( {1,1,1,1,1,1,1,1,1} ) // test case
		d_rep_per_mode( {2,4,1,8,2,4,3,2,4} )
{
	set_relative_rate(1.0/6.0);
}

void ofdm_puncture_bb::set_punctpat(char c_mode)
{
	unsigned int mode = (unsigned int)c_mode;

	if(!d_punctpat.empty())
	{
		d_punctpat.clear();
	}

	if(mode==1||mode==2||mode==4)
	{
		d_punctpat.push_back(1);
	}
	else if(mode==3||mode==5||mode==7||mode==9)
	{
		d_punctpat.push_back(1);
		d_punctpat.push_back(1);
		d_punctpat.push_back(0);
		d_punctpat.push_back(1);
		d_punctpat.push_back(1);
		d_punctpat.push_back(0);
	}
	else if(mode==6)
	{
		d_punctpat.push_back(1);
		d_punctpat.push_back(1);
		d_punctpat.push_back(0);
		d_punctpat.push_back(1);
	}
	else if(mode==8)
	{
		d_punctpat.push_back(1);
		d_punctpat.push_back(1);
		d_punctpat.push_back(0);
		d_punctpat.push_back(1);
		d_punctpat.push_back(1);
		d_punctpat.push_back(0);
		d_punctpat.push_back(0);
		d_punctpat.push_back(1);
		d_punctpat.push_back(1);
		d_punctpat.push_back(0);
	}
}
int
ofdm_puncture_bb::calc_bit_amount( const char* modemap, const int& vlen)
{
  int bits_per_symbol = 0;
  int size_per_mode[9] = {1,1,6,1,6,4,6,10,6};
  //int rep_per_mode[9] = {1,1,1,1,1,1,1,1,1};
  //int rep_per_mode[9] = {2,4,1,8,2,4,3,2,4};

  for(int i = 0; i < vlen; ++i) {
	if(modemap[i] > 9)
	  throw std::out_of_range("PUNCTURE: Mode higher than 9 not supported");
	if(modemap[i] < 0)
	  throw std::out_of_range("PUNCTURE: Cannot allocate less than zero bits");
	if(modemap[i] > 0)
		bits_per_symbol += size_per_mode[modemap[i]-1]*d_rep_per_mode[modemap[i]-1];
  }
  if(DEBUG)
           std::cout << "BITS_PER_SYMBOL: " << bits_per_symbol << " items" << std::endl;
  return bits_per_symbol;
}

int
ofdm_puncture_bb::calc_out_bit_amount( const char* modemap, const int& vlen)
{
  int out_bits_per_symbol = 0;
  //int size_per_mode[9] = {1,1,6,1,6,4,6,10,6};
  int out_size_per_mode[9] = {1,1,4,1,4,3,4,6,4};
  //int rep_per_mode[9] = {1,1,1,1,1,1,1,1,1};
  //int rep_per_mode[9] = {2,4,1,8,2,4,3,2,4};

  for(int i = 0; i < vlen; ++i) {
	if(modemap[i] > 9)
	  throw std::out_of_range("PUNCTURE: Mode higher than 9 not supported");
	if(modemap[i] < 0)
	  throw std::out_of_range("PUNCTURE: Cannot allocate less than zero bits");
	if(modemap[i] > 0)
		out_bits_per_symbol += out_size_per_mode[modemap[i]-1]*d_rep_per_mode[modemap[i]-1];
  }
  if(DEBUG)
           std::cout << "OUT_BITS_PER_SYMBOL: " << out_bits_per_symbol << " items" << std::endl;
  return out_bits_per_symbol;
}

void ofdm_puncture_bb::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
	ninput_items_required[0] = d_need_bits;
	ninput_items_required[1] = d_need_modemap;
	ninput_items_required[2] = std::ceil(noutput_items/d_vlen);
}

int ofdm_puncture_bb::general_work (int noutput_items,
		gr_vector_int &ninput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	unsigned int j;

	const char *in = static_cast<const char*>(input_items[0]);
	const char *modemap = static_cast<const char*>(input_items[1]);
	const char *trig = static_cast<const char*>(input_items[2]);
	char *out = static_cast<char*>(output_items[0]);

	int n_bits = ninput_items[0];
	int n_modemap = ninput_items[1];
	int n_trig = ninput_items[2];
	int nout = noutput_items;

	int noutsymbols = noutput_items;

	int n_min = std::min( nout, n_trig/d_vlen );

	if(DEBUG)
	std::cout << "[puncturing " << unique_id() << "] entered, state is "
			  << "n_bits=" << n_bits << " n_modemap=" << n_modemap
			  << " n_trig=" << n_trig << " nout=" << nout
			  << " d_need_bits=" << d_need_bits
			  << " d_out_bits=" << d_out_bits
			  << " d_need_modemap=" << d_need_modemap
			  << " n_min=" << n_min<< std::endl;

	bool copy = false;
	const char *map = d_modemap.get();

	  for( int i = 0; i < n_min; ++i, ++trig )
	  {
	    if( *trig != 0 )
	    {
	      if( n_modemap > 0 )
	      {
	        // update modemap buffer
	        map = modemap;

	        d_need_bits = calc_bit_amount( map, d_vlen );
	        d_out_bits = calc_out_bit_amount( map, d_vlen );

	        // if not enough input our output, won't consume trigger, therefore
	        // don't consume modemap item
	        if( n_bits < d_need_bits || nout < d_out_bits )
	        {
	          d_need_modemap = 1;
	          break;
	        }
	        copy = true;
	        d_need_modemap = 0;

	         --n_modemap;
	        modemap += d_vlen;
	        //consume(1, 1);	// consume modemap item

	        //if(DEBUG||n_modemap<100)
	        if(DEBUG)
	          std::cout << "Consume 1 modemap item, leave " << n_modemap << " items"
	                    << " and need " << d_need_bits << " bits while "
	                    << n_bits << " bits left and "
	                    << nout << " outputs left" << std::endl;
	      }
	      else
	      {
	        if(DEBUG)
	          std::cout << "Need modemap flag set" << std::endl;
	        d_need_modemap = 1;
	        break;
	      } // n_modemap > 0
	    } // *trig == 2
	    /*
	    else if( *trig == 1 )
	    {
	    	if( n_modemap > 0 )
	    	{
	    		//map = modemap;
	    		//copy = true;
	    		--n_modemap;
				//modemap += d_vlen;
				//consume(1, 1);	// consume modemap item
				consume(2, 1);	// consume this trigger
				d_need_modemap = 1;

				if(DEBUG)
				  std::cout << "Skip 1 modemap item, leave " << n_modemap << " items"
							<< " and need " << d_need_bits << " bits while "
							<< n_bits << " bits left and "
							<< nout << " outputs left" << std::endl;
				break;
	    	}
	    	else
	    	{
	    		if(DEBUG)
				  std::cout << "Need modemap flag set for skip trigger" << std::endl;
				d_need_modemap = 1;
				break;
	    	}
	    }*/

	    // check if we have enough bits

	    if( n_bits < d_need_bits ){
	      if(DEBUG)
	        std::cout << "Do not have enough bits, need " << d_need_bits
	                  << " have " << n_bits << std::endl;
	      break;
	    } // n_bits < d_need_bits

	    if( nout < d_out_bits ){
	 	      if(DEBUG)
	 	        std::cout << "Do not have enough output, need " << d_out_bits
	 	                  << " have " << nout << std::endl;
	 	      break;
	 	} // nout < d_out_bits

	    if( d_out_bits == 0 && d_need_bits == 0 ){
			  if(DEBUG)
				std::cout << "No usable modemap consumed, yet" << std::endl;
			  break;
		} // d_out_bits == 0 && d_need_bits == 0


	    if(DEBUG)
	         std::cout << ".";

	    // puncturing block
	    for( int i = 0; i < d_vlen; ++i )
	    {
	      if( map[i] > 0 )
	      {
	    	  if(map[i]==1||map[i]==2||map[i]==4)
	    	  {
	    		  //std::cout << "MAP ["<<i<<"]: "<<(float)map[i]<<std::endl;
	    		  for( int rep = 0; rep < d_rep_per_mode[map[i]-1]; ++rep )
	    		  {
	    			  *out++ = *in++;
	    			  --nout;
	    		  }

	    	  }
	    	  else
			  {
				  set_punctpat(map[i]);
				  //std::cout << "MAP ["<<i<<"]: "<<map[i]<<std::endl;
				  for( int rep = 0; rep < d_rep_per_mode[map[i]-1]; ++rep )
				  {
					  for (j=0;j<d_punctpat.size();j++)
				  {
					if (d_punctpat[j]==1)
					{
						*out++ = *in++;
						--nout;
					}
					else
					{
						in++;
					}
				  }
				  }
			  }
	      } // map[i] == 0
	    } // for-loop
	    n_bits -= d_need_bits;
	    noutsymbols--;
	  } // for-loop

	  // store to internal state variable
	  if( copy ){
	    memcpy( d_modemap.get(), map, d_vlen*sizeof(char) );
	    if(DEBUG)
	      std::cout << "Copy modemap to internal state buffer" << std::endl;
	  } // copy

	  //if(DEBUG||n_modemap<100)
	  if(DEBUG)
	    std::cout << "[puncture] Leaving process, d_need_bits=" << d_need_bits
	              << " d_need_modemap=" << d_need_modemap << " consume "
	              << ninput_items[0]-n_bits << " bits and produce "
	              << noutput_items-nout << " bits\n and "
	              << noutput_items-noutsymbols << " symbols\n"
	              << std::endl;

	  consume(0, ninput_items[0]-n_bits);	 // consume input bits
	  consume(1, ninput_items[1]-n_modemap);
	  consume(2, noutput_items-noutsymbols); // consume trigger items

	  return noutput_items-nout;
}

int
ofdm_puncture_bb::noutput_forecast( gr_vector_int &ninput_items,
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{

  if( ninput_items[0] < d_need_bits ){
    if( input_done[0] ){
      return -1;
    }

    return 0;
  }

  if( ninput_items[1] < d_need_modemap ){
    if( input_done[1] ){
      return -1;
    }

    return 0;
  }

  if( ninput_items[2] == 0 && input_done[2] ){
    return -1;
  }

  return std::min( available_space, ninput_items[2] );

}
