#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_gate_ff.h>

#include <cstdlib>

ofdm_gate_ff_sptr ofdm_make_gate_ff ()
{
	return ofdm_gate_ff_sptr (new ofdm_gate_ff ());
}

ofdm_gate_ff::ofdm_gate_ff ()
	: gr_sync_block ("gate_ff",
			gr_make_io_signature2 (1, -1, sizeof(char), sizeof(float)),
			gr_make_io_signature2 (1, -1, sizeof(char), sizeof(float)))
{
}

int ofdm_gate_ff::work (int noutput_items,	
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const char *in = static_cast<const char*>(input_items[0]);
	
	assert(input_items.size() == output_items.size());
	
	int j = 0;
	for(int i = 0; i < noutput_items; ++i) {
		if(in[i] == 1) {
			(static_cast<char*>(output_items[0]))[j] = in[i];
			for(std::size_t s = 1; s < output_items.size(); ++s) {
				(static_cast<float*>(output_items[s]))[j] = (static_cast<const float*>(input_items[s]))[i];
			}
			++j;
		}
	}
	
	consume_each(noutput_items - j);
	return j;
}
