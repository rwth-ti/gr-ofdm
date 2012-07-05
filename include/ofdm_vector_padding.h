#ifndef INCLUDED_OFDM_VECTOR_PADDING_H_
#define INCLUDED_OFDM_VECTOR_PADDING_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>
#include <gr_sync_block.h>

#include <vector>
#include <boost/shared_array.hpp>

class ofdm_vector_padding;
typedef boost::shared_ptr<ofdm_vector_padding> ofdm_vector_padding_sptr;

OFDM_API ofdm_vector_padding_sptr ofdm_make_vector_padding (int carriers, int vlen, int padding_left = -1);

/**
 * @brief Pad vector with zeroes on left and right
 */
class OFDM_API ofdm_vector_padding : public gr_sync_block
{
	private:
		friend OFDM_API ofdm_vector_padding_sptr 
			ofdm_make_vector_padding (int carriers, int vlen, int padding_left);
		
		ofdm_vector_padding (int carriers, int vlen, int padding_left);

		int d_carriers, d_vlen, d_padding_left;

	public:
		virtual ~ofdm_vector_padding() {};
		
		int work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items);
};
	 

#endif /* INCLUDED_OFDM_VECTOR_PADDING_H_ */
