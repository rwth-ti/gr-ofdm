#ifndef INCLUDED_OFDM_VECTOR_SUM_VCC_H_
#define INCLUDED_OFDM_VECTOR_SUM_VCC_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_vector_sum_vcc;
typedef boost::shared_ptr<ofdm_vector_sum_vcc> ofdm_vector_sum_vcc_sptr;
OFDM_API ofdm_vector_sum_vcc_sptr ofdm_make_vector_sum_vcc(int vlen);

/*!
 * Compute sum over vector elements
 *
 * For each input vector, sum over vector elements and output sum.
 */
class OFDM_API ofdm_vector_sum_vcc : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_vector_sum_vcc_sptr ofdm_make_vector_sum_vcc(int vlen);

    ofdm_vector_sum_vcc(int vlen);

    int  d_vlen;

  public:
    virtual ~ofdm_vector_sum_vcc() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_VECTOR_SUM_VCC_H_ */
