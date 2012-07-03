#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_interpolator.h>
#include <gr_io_signature.h>
#include <ofdm_repetition_encoder_sb.h>
#include <iostream>

#define DEBUG 0

ofdm_repetition_encoder_sb_sptr ofdm_make_repetition_encoder_sb(unsigned short input_bits, unsigned short repetitions, std::vector<int> whitener)
{
  return ofdm_repetition_encoder_sb_sptr(new ofdm_repetition_encoder_sb(input_bits, repetitions, whitener));
}

ofdm_repetition_encoder_sb::ofdm_repetition_encoder_sb(unsigned short input_bits, unsigned short repetitions, std::vector<int> whitener)
  : gr_sync_interpolator("repetition_encoder_sb",
           gr_make_io_signature (1, 1, sizeof(short)),
           gr_make_io_signature (1, 1, sizeof(char)),
           input_bits * repetitions),
  d_input_bits(input_bits), d_repetitions(repetitions), d_whitener(whitener)
{
  for(std::vector<int>::const_iterator iter = d_whitener.begin(); iter != d_whitener.end(); ++iter){
    assert(*iter == 0 || *iter == 1);
  }
  
  if(DEBUG)
    std::cout << "[rep enc " << unique_id() << "] input_bits=" << input_bits
              << " repetitions=" << repetitions << std::endl;
}

int ofdm_repetition_encoder_sb::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const short *in = static_cast<const short*>(input_items[0]);
  char *out = static_cast<char*>(output_items[0]);
  unsigned int output_pos = 0;
  
  if(DEBUG)
    std::cout << "[rep enc " << unique_id() << "] entered, "
              << "nout=" << noutput_items << std::endl;

  //iterate over all input items
  for (int item = 0; item < (noutput_items / (d_input_bits * d_repetitions)); item++)
  {
	  //repeat the input d_repetitions times
	  for (unsigned short reps = 0; reps < d_repetitions; reps++)
	  {
		  //and write it bit by bit to the output
		  for (unsigned short bit = 0; bit < d_input_bits; bit++)
		  {
			  out[output_pos++] = ((char)(in[item] >> bit)) & 1
			                      ^ d_whitener[reps*d_input_bits+bit];
		  }
	  }
  }
  
  if(DEBUG)
    std::cout << "[rep enc] leave, produce " << output_pos << " items"
              << std::endl;
  
  return output_pos;
}
