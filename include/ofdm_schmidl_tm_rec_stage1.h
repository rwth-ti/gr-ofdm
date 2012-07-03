#ifndef INCLUDED_OFDM_SCHMIDL_TM_REC_STAGE1_H_
#define INCLUDED_OFDM_SCHMIDL_TM_REC_STAGE1_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_schmidl_tm_rec_stage1;
typedef boost::shared_ptr<ofdm_schmidl_tm_rec_stage1> ofdm_schmidl_tm_rec_stage1_sptr;
OFDM_API ofdm_schmidl_tm_rec_stage1_sptr ofdm_make_schmidl_tm_rec_stage1(int fft_length);

/*!

 */
class OFDM_API ofdm_schmidl_tm_rec_stage1 : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_schmidl_tm_rec_stage1_sptr ofdm_make_schmidl_tm_rec_stage1(int fft_length);

    ofdm_schmidl_tm_rec_stage1(int fft_length);

    int  d_fft_length;
    int  d_delay;
 
  public:
    virtual ~ofdm_schmidl_tm_rec_stage1() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_SCHMIDL_TM_REC_STAGE1_H_ */
