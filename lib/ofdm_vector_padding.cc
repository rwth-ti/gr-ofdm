#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>

#include <ofdm_vector_padding.h>
#include <gr_io_signature.h>
#include <gr_math.h>

#include <string.h>


#include <vector>
#include <iostream>

//#define DEBUG(x) x
#define DEBUG(x)

ofdm_vector_padding_sptr ofdm_make_vector_padding (int carriers, int vlen, int padding_left /* = -1 */)
{
	return ofdm_vector_padding_sptr(new ofdm_vector_padding(carriers, vlen, padding_left));
}

ofdm_vector_padding::ofdm_vector_padding (int carriers, int vlen, int padding_left)
	: gr_sync_block("ofdm_vector_padding",
				gr_make_io_signature(1, 1, sizeof(gr_complex) * carriers),
				gr_make_io_signature(1, 1, sizeof(gr_complex) * vlen)),
		d_carriers(carriers), d_vlen(vlen), d_padding_left(padding_left)
{
	if(d_padding_left < 0) {
		d_padding_left = static_cast<int>(ceil((d_vlen - d_carriers) / 2.0));
	}
	assert(vlen >= d_padding_left + carriers);
}

int ofdm_vector_padding::work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items)
{
	DEBUG(std::cout << "padding input: " <<  noutput_items << std::endl;)

	const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
	gr_complex *out = static_cast<gr_complex*>(output_items[0]);

	/* fill unused carriers in first ofdm symbol */
	gr_complex complex_zero(0,0);
	int i;
	for(i = 0; i < d_padding_left; ++i) {
		out[i] = complex_zero;
	}
	for(i+= d_carriers; i < d_vlen; ++i) {
		out[i] = complex_zero;
	}

	gr_complex *shifted_out = out + d_padding_left;
	memcpy(shifted_out , in, d_carriers * sizeof(gr_complex));
	shifted_out += d_vlen;
	in+= d_carriers;

	/* copy that shape to every ofdm symbol */
	for(i = 1; i < noutput_items; ++i, shifted_out += d_vlen, in+= d_carriers) {
		memcpy(out + i*d_vlen, out, d_vlen * sizeof(gr_complex));
		memcpy(shifted_out , in, d_carriers * sizeof(gr_complex));
	}

	return noutput_items;
}

