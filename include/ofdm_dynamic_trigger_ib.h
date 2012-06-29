#ifndef INCLUDED_OFDM_DYNAMIC_TRIGGER_IB_H_
#define INCLUDED_OFDM_DYNAMIC_TRIGGER_IB_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_block.h>

class ofdm_dynamic_trigger_ib;
typedef boost::shared_ptr<ofdm_dynamic_trigger_ib> ofdm_dynamic_trigger_ib_sptr;
OFDM_API ofdm_dynamic_trigger_ib_sptr ofdm_make_dynamic_trigger_ib(bool first_or_last);

/*!
 * \brief Generate trigger impulses dynamically spaced
 * 
 * Input: next trigger window size (e.g. from bitcount source etc.)
 * Output: segmented byte stream, each segment size equals input window size
 * specification. Either first or last byte is set to 1, all other are 0.
 */
class OFDM_API ofdm_dynamic_trigger_ib : public gr_block
{
  private:
    friend OFDM_API ofdm_dynamic_trigger_ib_sptr ofdm_make_dynamic_trigger_ib(bool first_or_last);

    ofdm_dynamic_trigger_ib(bool first_or_last);

    bool  d_first_or_last;
    unsigned int d_produced;
 
    void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  public:
    virtual ~ofdm_dynamic_trigger_ib() {};

    int general_work(
      int noutput_items,
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
    
    virtual int noutput_forecast( gr_vector_int &ninput_items, 
        int available_space, int max_items_avail,
        std::vector<bool> &input_done );
};

#endif /* INCLUDED_OFDM_DYNAMIC_TRIGGER_IB_H_ */
