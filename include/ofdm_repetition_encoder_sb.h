#ifndef INCLUDED_OFDM_REPETITION_ENCODER_SB_H_
#define INCLUDED_OFDM_REPETITION_ENCODER_SB_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_interpolator.h>

class ofdm_repetition_encoder_sb;
typedef boost::shared_ptr<ofdm_repetition_encoder_sb> ofdm_repetition_encoder_sb_sptr;
OFDM_API ofdm_repetition_encoder_sb_sptr ofdm_make_repetition_encoder_sb(unsigned short input_bits, unsigned short repetitions, std::vector<int> whitener);

/*!

 */
class OFDM_API ofdm_repetition_encoder_sb : public gr_sync_interpolator
{
  private:
    friend OFDM_API ofdm_repetition_encoder_sb_sptr ofdm_make_repetition_encoder_sb(unsigned short input_bits, unsigned short repetitions, std::vector<int> whitener);

    ofdm_repetition_encoder_sb(unsigned short input_bits, unsigned short repetitions, std::vector<int> whitener);

    short  d_input_bits;
    short  d_repetitions;
    std::vector<int> d_whitener;

  public:
    virtual ~ofdm_repetition_encoder_sb() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_REPETITION_ENCODER_SB_H_ */
