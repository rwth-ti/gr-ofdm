#ifndef INCLUDED_OFDM_stream_controlled_mux_b_H_
#define INCLUDED_OFDM_stream_controlled_mux_b_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_block.h>

class ofdm_stream_controlled_mux_b;
typedef boost::shared_ptr<ofdm_stream_controlled_mux_b> ofdm_stream_controlled_mux_b_sptr;
OFDM_API ofdm_stream_controlled_mux_b_sptr ofdm_make_stream_controlled_mux_b();

/*!
 * \brief Input stream controls multiplexing
 *
 * For each item on input 1, one item from a selected input is multiplexed
 * in the output. Items in 1 should be in range (0,#mux_ports-1).
 */
class OFDM_API ofdm_stream_controlled_mux_b : public gr_block
{
  private:
    friend OFDM_API ofdm_stream_controlled_mux_b_sptr ofdm_make_stream_controlled_mux_b();

    ofdm_stream_controlled_mux_b();

    unsigned int d_next_input;

    void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  public:
    virtual ~ofdm_stream_controlled_mux_b() {};

    int general_work(
      int noutput_items,
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
    
    virtual int noutput_forecast( gr_vector_int &ninput_items, 
        int available_space, int max_items_avail,
        std::vector<bool> &input_done );
};

#endif /* INCLUDED_OFDM_stream_controlled_mux_b_H_ */
