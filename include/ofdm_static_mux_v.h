#ifndef INCLUDED_OFDM_STATIC_MUX_V_H_
#define INCLUDED_OFDM_STATIC_MUX_V_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_block.h>

class ofdm_static_mux_v;
typedef boost::shared_ptr<ofdm_static_mux_v> ofdm_static_mux_v_sptr;

OFDM_API ofdm_static_mux_v_sptr
ofdm_make_static_mux_v( int streamsize, const std::vector<int> &mux_ctrl );

/*!

 */
class OFDM_API ofdm_static_mux_v : public gr_block
{
  private:
    friend OFDM_API ofdm_static_mux_v_sptr
    ofdm_make_static_mux_v( int streamsize, const std::vector<int> &mux_ctrl );

    ofdm_static_mux_v( int streamsize, const std::vector<int> &mux_ctrl );

    int                 d_streamsize;
    std::vector<int>    d_mux_ctrl;
    int                 d_mpos;
    int                 d_msize;

    void forecast( int noutput_items, gr_vector_int &ninput_items_required );

  public:
    virtual ~ofdm_static_mux_v() {};

    virtual bool check_topology( int ninputs, int noutputs );

    void reset() { d_mpos = 0; }

    int general_work(
      int noutput_items,
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);

    virtual int noutput_forecast( gr_vector_int &ninput_items,
        int available_space, int max_items_avail,
        std::vector<bool> &input_done );

};

#endif /* INCLUDED_OFDM_STATIC_MUX_V_H_ */
