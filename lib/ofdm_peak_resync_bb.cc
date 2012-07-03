#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>

#include "ofdm_peak_resync_bb.h"
#include <gr_io_signature.h>

#include <algorithm>
#include <iostream>

//#define DEBUG(x) x
#define DEBUG(x)

ofdm_peak_resync_bb_sptr ofdm_make_peak_resync_bb (bool replace)
{
	return ofdm_peak_resync_bb_sptr (new ofdm_peak_resync_bb (replace));
}

ofdm_peak_resync_bb::ofdm_peak_resync_bb (bool replace)
	: gr_block ("peak_resync_bb",
		       gr_make_io_signature (2, 2, sizeof(char)),
		       gr_make_io_signature (1, 1, sizeof(char))),
		d_replace(replace), d_resync(0)
{
}

void ofdm_peak_resync_bb::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
	ninput_items_required[0] = noutput_items;
	ninput_items_required[1] = d_resync;
}

int ofdm_peak_resync_bb::general_work (int noutput_items,
		gr_vector_int &ninput_items,		
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items)
{
	const char *in = static_cast<const char*>(input_items[0]);
	const char *in_2 = static_cast<const char*>(input_items[1]);
	char *out = static_cast<char*>(output_items[0]);
	
	if(d_resync > 0 && ninput_items[1] == 0)
		/* we need at least one item from the second stream */
		return 0;	
	
	const int nitems = std::min(ninput_items[0], noutput_items);
	int nitems_2 = ninput_items[1];
	
	int i, j;
	for(i = 0, j = 0; i < nitems; ++i) {
		if(in[i] == 1) {
			/* we got a peak */
			if(nitems_2 > 0) {
				/* we can consume one more item from the second stream */
				out[i] = d_replace ? in_2[j++] : in [i];
				d_resync = 0;
				--nitems_2;
			} else {
				/* there are no items from the second stream available, so we wait */				
				if(i > 0)
					consume(0, i); /* consume up to the item before the peak */
				if(j > 0)
					consume(1, j);
				
				d_resync = 1;
				DEBUG(std::cout << "waiting for second stream, passed up " << i << " and consumed " << j << std::endl;)
				return i;
			}
		} else {
			out[i] = in[i];
		}
	}

	DEBUG(std::cout << "consumed " << i << " and " << j << std::endl;)
	
	/* tell the system what we consumed */
	if(i > 0)
		consume(0, i);	
	if(j > 0)
		consume(1, j);

	return i;				
}
