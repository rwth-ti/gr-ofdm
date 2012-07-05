#ifndef INCLUDED_OFDM_SC_SNR_ESTIMATOR_H_
#define INCLUDED_OFDM_SC_SNR_ESTIMATOR_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_sc_snr_estimator;
typedef boost::shared_ptr<ofdm_sc_snr_estimator> ofdm_sc_snr_estimator_sptr;
OFDM_API ofdm_sc_snr_estimator_sptr ofdm_make_sc_snr_estimator(int vlen);

/*!
 * \brief SNR Estimator with Schmidl & Cox Algorithm
 * 
 * This is the implementation of the Schmidl & Cox algorithm for estimating
 * the SNR based on a periodic preamble. See the paper for more details.
 * 
 * The algorithm is not numerically stable. Therefore this block additionally
 * limits the output values to an acceptable range.
 * 
 * Damn it! This is heavily numerically unstable!!
 */
class OFDM_API ofdm_sc_snr_estimator : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_sc_snr_estimator_sptr ofdm_make_sc_snr_estimator(int vlen);

    ofdm_sc_snr_estimator(int vlen);

    int  d_vlen;
 
  public:
    virtual ~ofdm_sc_snr_estimator() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_SC_SNR_ESTIMATOR_H_ */
