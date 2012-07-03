#ifndef INCLUDED_OFDM_SCHMIDL_TM_REC_STAGE2_H_
#define INCLUDED_OFDM_SCHMIDL_TM_REC_STAGE2_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_schmidl_tm_rec_stage2;
typedef boost::shared_ptr<ofdm_schmidl_tm_rec_stage2> ofdm_schmidl_tm_rec_stage2_sptr;
OFDM_API ofdm_schmidl_tm_rec_stage2_sptr ofdm_make_schmidl_tm_rec_stage2( int window );

/*!

 */
class OFDM_API ofdm_schmidl_tm_rec_stage2 : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_schmidl_tm_rec_stage2_sptr ofdm_make_schmidl_tm_rec_stage2( int window );

    ofdm_schmidl_tm_rec_stage2( int window );

    int         d_delay;

    gr_complex  d_acc1;
    float       d_acc2;

  public:
    virtual ~ofdm_schmidl_tm_rec_stage2() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_SCHMIDL_TM_REC_STAGE2_H_ */
