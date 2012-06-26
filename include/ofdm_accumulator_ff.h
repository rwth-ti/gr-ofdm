#ifndef INCLUDED_OFDM_ACCUMULATOR_FF_H_
#define INCLUDED_OFDM_ACCUMULATOR_FF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_block.h>

class ofdm_accumulator_ff;
typedef boost::shared_ptr<ofdm_accumulator_ff> ofdm_accumulator_ff_sptr;
OFDM_API ofdm_accumulator_ff_sptr ofdm_make_accumulator_ff();

/*!

 */
class OFDM_API ofdm_accumulator_ff : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_accumulator_ff_sptr ofdm_make_accumulator_ff();

    ofdm_accumulator_ff();

    float d_accum;


  public:
    virtual ~ofdm_accumulator_ff() {};

    void reset() { d_accum = 0.0; }

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_ACCUMULATOR_FF_H_ */
