#ifndef INCLUDED_OFDM_ACCUMULATOR_CC_H_
#define INCLUDED_OFDM_ACCUMULATOR_CC_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h" // forward declarations --specific
#include <gr_block.h>

class ofdm_accumulator_cc;
typedef boost::shared_ptr<ofdm_accumulator_cc> ofdm_accumulator_cc_sptr;
OFDM_API ofdm_accumulator_cc_sptr ofdm_make_accumulator_cc();

/*!

 */

class OFDM_API ofdm_accumulator_cc : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_accumulator_cc_sptr ofdm_make_accumulator_cc();

    ofdm_accumulator_cc();

    gr_complex d_accum;


  public:

    void reset() { d_accum = gr_complex(0.0,0.0); }

    virtual ~ofdm_accumulator_cc() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_ACCUMULATOR_CC_H_ */
