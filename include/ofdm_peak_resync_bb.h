#ifndef INCLUDED_OFDM_PEAK_RESYNC_BB_H_
#define INCLUDED_OFDM_PEAK_RESYNC_BB_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_block.h>

class ofdm_peak_resync_bb;
typedef boost::shared_ptr<ofdm_peak_resync_bb> ofdm_peak_resync_bb_sptr;
OFDM_API ofdm_peak_resync_bb_sptr ofdm_make_peak_resync_bb (bool replace);

/*!
  This block resynchronizes two streams. First stream should be a stream of
  peaks/trigger events and second stream should be triggered asynchronously by
  the first stream, than for example handled in some different ways.
  
  For every peak in the first stream, we will consume one item
  of the second stream. If you specified to @param replace, then the peak
  in the first stream will be replaced by the consumed item from the second
  stream.
 */
class OFDM_API ofdm_peak_resync_bb : public gr_block
{
	private:
		friend OFDM_API ofdm_peak_resync_bb_sptr ofdm_make_peak_resync_bb (bool replace);		
		
		ofdm_peak_resync_bb (bool replace);		
 
		void forecast (int noutput_items, gr_vector_int &ninput_items_required);
		
		bool d_replace;
		int d_resync; //<! holds amount of items we are waiting for

	public:
		virtual ~ofdm_peak_resync_bb() {};
		
		int general_work (int noutput_items,
			gr_vector_int &ninput_items,		
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_PEAK_RESYNC_BB_H_ */
