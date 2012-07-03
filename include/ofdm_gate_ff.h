#ifndef INCLUDED_OFDM_GATE_FF_H_
#define INCLUDED_OFDM_GATE_FF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_gate_ff;
typedef boost::shared_ptr<ofdm_gate_ff> ofdm_gate_ff_sptr;
OFDM_API ofdm_gate_ff_sptr ofdm_make_gate_ff ();

/*!
  This block gates its input streams. If the trigger stream (input #0) is
  below the threshold (i.e. <0.5), no output items will be produced. On the 
  other side, if input 0 is >= threshold, every stream will pass through.
  Streams are consumed at the same input rate.
  
  Trigger stream: char
  Other streams: float
 */
class OFDM_API ofdm_gate_ff : public gr_sync_block
{
	private:
		friend OFDM_API ofdm_gate_ff_sptr ofdm_make_gate_ff ();
		
		ofdm_gate_ff ();
 
	public:
		virtual ~ofdm_gate_ff() {};
		
		int work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_GATE_FF_H_ */
