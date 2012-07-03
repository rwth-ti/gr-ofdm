#ifndef INCLUDED_OFDM_MM_FREQUENCY_ESTIMATOR_H_
#define INCLUDED_OFDM_MM_FREQUENCY_ESTIMATOR_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

#include <vector>

class ofdm_mm_frequency_estimator;
typedef boost::shared_ptr<ofdm_mm_frequency_estimator> ofdm_mm_frequency_estimator_sptr;
OFDM_API ofdm_mm_frequency_estimator_sptr ofdm_make_mm_frequency_estimator(int vlen, 
    int identical_parts);

/*! 
 * \brief Frequency Offset estimator with Morelli & Mengali algorithm
 * 
 * Based on preambles with several identical parts, the algorithm estimates
 * an existing frequency offset in the range of [-L/2, L/2] where 
 * L = \param identical_parts. See the paper for more details.
 * 
 * Simply said we use the correlation between the parts and put them in
 * weighted sum, where the weights more or less define our confidence
 * in this particular value.
 */
class OFDM_API ofdm_mm_frequency_estimator : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_mm_frequency_estimator_sptr ofdm_make_mm_frequency_estimator(int vlen,
        int identical_parts);

    ofdm_mm_frequency_estimator(int vlen, int identical_parts);

    int  d_vlen;
    int  d_L;
    int  d_M;
    
    std::vector<float> d_weights;
    
 
  public:
    virtual ~ofdm_mm_frequency_estimator() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_MM_FREQUENCY_ESTIMATOR_H_ */
