#ifndef INCLUDED_OFDM_SQRT_VFF_H_
#define INCLUDED_OFDM_SQRT_VFF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_sqrt_vff;
typedef boost::shared_ptr<ofdm_sqrt_vff> ofdm_sqrt_vff_sptr;
OFDM_API ofdm_sqrt_vff_sptr ofdm_make_sqrt_vff (int vlen);

/*!

 */
class OFDM_API ofdm_sqrt_vff : public gr_sync_block
{
	private:
		friend OFDM_API ofdm_sqrt_vff_sptr ofdm_make_sqrt_vff (int vlen);		
		
		ofdm_sqrt_vff (int vlen);
		
		int d_vlen;
 
	public:
		virtual ~ofdm_sqrt_vff() {};
		
		int work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_SQRT_VFF_H_ */
