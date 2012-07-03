#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_decimator.h>
#include <gr_io_signature.h>
#include <ofdm_repetition_decoder_bs.h>

#include <iostream>


ofdm_repetition_decoder_bs_sptr ofdm_make_repetition_decoder_bs(unsigned short output_bits, unsigned short repetitions, std::vector<int> whitener)
{
  return ofdm_repetition_decoder_bs_sptr(new ofdm_repetition_decoder_bs(output_bits, repetitions, whitener));
}

ofdm_repetition_decoder_bs::ofdm_repetition_decoder_bs(unsigned short output_bits, unsigned short repetitions, std::vector<int> whitener)
  : gr_sync_decimator("repetition_decoder_bs",
           gr_make_io_signature (1, 1, sizeof(char)),
           gr_make_io_signature (1, 1, sizeof(short)),
           output_bits * repetitions),
  d_output_bits(output_bits), d_repetitions(repetitions), d_whitener(whitener)
{
  assert(d_whitener.size() == d_repetitions*d_output_bits);
  for(std::vector<int>::const_iterator iter = d_whitener.begin(); iter != d_whitener.end(); ++iter){
    assert(*iter == 0 || *iter == 1);
  }
}

int ofdm_repetition_decoder_bs::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
	//std::cout << "Start decoding work" << std::endl;
  const char *in = static_cast<const char*>(input_items[0]);
  short *out = static_cast<short*>(output_items[0]);
  unsigned int output_pos = 0;
  unsigned int input_pos = 0;

  std::vector<unsigned short> decision_vector;

  //iterate over all items (where item is d_repetitions * d_output_bits bytes)
  for (unsigned int item = 0; item < noutput_items ; item++)
  {
	  //fill decision vector with d_output_bits zeros
	  decision_vector.resize(0, 0);
	  decision_vector.resize(d_output_bits, 0);

	  //std::cout << "my input bits are " << std::endl;
	  //iterate over all repetitions
	  for(unsigned short rep = 0; rep < d_repetitions; rep++)
	  {
		  //iterate over bits
		  for(unsigned short bit = 0; bit < d_output_bits; bit++)
		  {
		//    std::cout << (int)(in[input_pos]^ d_whitener[rep*d_output_bits+bit]);
			  decision_vector[bit] += in[input_pos++]
			                          ^ d_whitener[rep*d_output_bits+bit];

		  }
		  //std::cout << std::endl;
	  }
	  // Now for every position every "vote" was taken ...
	  unsigned short tempVal = 0;
	  for (unsigned short i = 0; i < d_output_bits; i++)
	  {
		  if(decision_vector[i] > (d_repetitions/2))
		  {
			  tempVal = tempVal | (1 << i);
		  }
		  else
		  {
			  //Commented out because not doing anything
			  //tempVal = tempVal || (0 << i);
		  }
	  }
#ifdef DEBUG_OUT
	  std::cout << "Decoded ID: " << tempVal << std::endl;
#endif
	  out[output_pos++] = tempVal;

  }
  //std::cout << "Decoder returned " << output_pos << " items" << std::endl;
  return output_pos;
}
