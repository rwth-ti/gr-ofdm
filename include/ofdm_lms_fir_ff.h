#ifndef INCLUDED_OFDM_LMS_FIR_FF_H_
#define INCLUDED_OFDM_LMS_FIR_FF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_lms_fir_ff;
typedef boost::shared_ptr<ofdm_lms_fir_ff> ofdm_lms_fir_ff_sptr;
OFDM_API ofdm_lms_fir_ff_sptr ofdm_make_lms_fir_ff (int len, float mu);

#include <boost/shared_array.hpp>

/*!

 */
class OFDM_API ofdm_lms_fir_ff : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_lms_fir_ff_sptr ofdm_make_lms_fir_ff (int len, float mu);

    ofdm_lms_fir_ff (int len, float mu);

    int d_len;
    float d_mu;
    boost::shared_array<float> d_taps;

  public:
    virtual ~ofdm_lms_fir_ff() {};

    int work (int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_LMS_FIR_FF_H_ */
