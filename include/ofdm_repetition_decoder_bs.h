#ifndef INCLUDED_OFDM_REPETITION_DECODER_BS_H_
#define INCLUDED_OFDM_REPETITION_DECODER_BS_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <vector>
#include <gr_sync_decimator.h>

class ofdm_repetition_decoder_bs;
typedef boost::shared_ptr<ofdm_repetition_decoder_bs> ofdm_repetition_decoder_bs_sptr;
OFDM_API ofdm_repetition_decoder_bs_sptr ofdm_make_repetition_decoder_bs(unsigned short output_bits, unsigned short repetitions, std::vector<int> whitener);

/*!

 */
class OFDM_API ofdm_repetition_decoder_bs : public gr_sync_decimator
{
  private:
    friend OFDM_API ofdm_repetition_decoder_bs_sptr ofdm_make_repetition_decoder_bs(unsigned short output_bits, unsigned short repetitions, std::vector<int> whitener);

    ofdm_repetition_decoder_bs(unsigned short output_bits, unsigned short repetitions, std::vector<int> whitener);

    short  d_output_bits;
    short  d_repetitions;

    std::vector<int> d_whitener;

  public:
    virtual ~ofdm_repetition_decoder_bs() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_REPETITION_DECODER_BS_H_ */
