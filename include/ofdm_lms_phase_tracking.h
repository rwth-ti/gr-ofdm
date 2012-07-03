#ifndef INCLUDED_OFDM_LMS_PHASE_TRACKING_H_
#define INCLUDED_OFDM_LMS_PHASE_TRACKING_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_lms_phase_tracking;
typedef boost::shared_ptr<ofdm_lms_phase_tracking>
    ofdm_lms_phase_tracking_sptr;
OFDM_API ofdm_lms_phase_tracking_sptr ofdm_make_lms_phase_tracking(int vlen,
    const std::vector<int> &pilot_tones,
    const std::vector<int> &data_symbols);

/*!
 * \brief Phase tracking to correct SFO in freq. domain
 * 
 * Input:
 *  1. OFDM blocks, frequency domain
 *  2. frame trigger
 * 
 * 
 */
class OFDM_API ofdm_lms_phase_tracking : public gr_sync_block
{
private:
  friend OFDM_API ofdm_lms_phase_tracking_sptr ofdm_make_lms_phase_tracking(
      int vlen, const std::vector<int> &pilot_tones,
      const std::vector<int> &data_symbols);

  ofdm_lms_phase_tracking(int vlen,
      const std::vector<int> &pilot_tones,
      const std::vector<int> &data_symbols);

  int d_blk;
  int d_dblk;

  int d_vlen;
  std::vector<bool> d_is_data_symbol;

  int d_pcount;
  std::vector<float> d_pilot_tone;
  std::vector<int> d_pilot;

  std::vector<float> d_gamma_coeff;
  //std::vector<float> d_b_coeff;

  std::vector<float> d_acc_phase;
  std::vector<bool> d_is_pilot;
  

public:
  virtual ~ofdm_lms_phase_tracking() {};

  int work(int noutput_items, gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_LMS_PHASE_TRACKING_H_ */
