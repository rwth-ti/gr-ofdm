#ifndef INCLUDED_OFDM_static_mux_c_H_
#define INCLUDED_OFDM_static_mux_c_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_block.h>

class ofdm_static_mux_c;
typedef boost::shared_ptr<ofdm_static_mux_c> ofdm_static_mux_c_sptr;

OFDM_API ofdm_static_mux_c_sptr 
ofdm_make_static_mux_c( const std::vector<int> &mux_ctrl );

/*!

 */
class OFDM_API ofdm_static_mux_c : public gr_block
{
  private:
    friend OFDM_API ofdm_static_mux_c_sptr 
    ofdm_make_static_mux_c( const std::vector<int> &mux_ctrl );

    ofdm_static_mux_c( const std::vector<int> &mux_ctrl );

    std::vector<int>    d_mux_ctrl;
    int                 d_mpos;
    int                 d_msize;
 
    void forecast( int noutput_items, gr_vector_int &ninput_items_required );

  public:
    virtual ~ofdm_static_mux_c() {};
    
    virtual bool check_topology( int ninputs, int noutputs );

    int general_work(
      int noutput_items,
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
    
    virtual int noutput_forecast( gr_vector_int &ninput_items, 
        int available_space, int max_items_avail,
        std::vector<bool> &input_done );
};

#endif /* INCLUDED_OFDM_static_mux_c_H_ */
