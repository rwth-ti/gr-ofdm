#ifndef INCLUDED_OFDM_NORMALIZE_VCC_H_
#define INCLUDED_OFDM_NORMALIZE_VCC_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_normalize_vcc;
typedef boost::shared_ptr<ofdm_normalize_vcc> ofdm_normalize_vcc_sptr;
OFDM_API ofdm_normalize_vcc_sptr ofdm_make_normalize_vcc (int vlen, float norm_power);

/*!

 */
class OFDM_API ofdm_normalize_vcc : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_normalize_vcc_sptr ofdm_make_normalize_vcc (int vlen, float norm_power);

    ofdm_normalize_vcc (int vlen, float norm_power);

    float d_norm_power;
    int d_vlen;

  public:
    virtual ~ofdm_normalize_vcc() {};

    int work (int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_NORMALIZE_VCC_H_ */
