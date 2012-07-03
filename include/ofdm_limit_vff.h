#ifndef INCLUDED_OFDM_LIMIT_VFF_H_
#define INCLUDED_OFDM_LIMIT_VFF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_limit_vff;
typedef boost::shared_ptr<ofdm_limit_vff> ofdm_limit_vff_sptr;
OFDM_API ofdm_limit_vff_sptr ofdm_make_limit_vff(int vlen, float up_limit, float lo_limit);

/*!

 */
class OFDM_API ofdm_limit_vff : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_limit_vff_sptr ofdm_make_limit_vff(int vlen,
        float up_limit, float lo_limit);

    ofdm_limit_vff(int vlen, float up_limit, float lo_limit);

    float d_up_limit;
    float d_lo_limit;
    int d_vlen;

  public:
    virtual ~ofdm_limit_vff() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_LIMIT_VFF_H_ */
