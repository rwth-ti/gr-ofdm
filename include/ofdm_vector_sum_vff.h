#ifndef INCLUDED_OFDM_VECTOR_SUM_VFF_H_
#define INCLUDED_OFDM_VECTOR_SUM_VFF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_vector_sum_vff;
typedef boost::shared_ptr<ofdm_vector_sum_vff> ofdm_vector_sum_vff_sptr;
OFDM_API ofdm_vector_sum_vff_sptr ofdm_make_vector_sum_vff(int vlen);

/*!

 */
class OFDM_API ofdm_vector_sum_vff : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_vector_sum_vff_sptr ofdm_make_vector_sum_vff(int vlen);

    ofdm_vector_sum_vff(int vlen);

    int  d_vlen;
 
  public:
    virtual ~ofdm_vector_sum_vff() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_VECTOR_SUM_VFF_H_ */
