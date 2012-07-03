#ifndef INCLUDED_OFDM_GET_ZEROS_H_
#define INCLUDED_OFDM_GET_ZEROS_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_sync_block.h>

class ofdm_get_zeros;
typedef boost::shared_ptr<ofdm_get_zeros> ofdm_get_zeros_sptr;
OFDM_API ofdm_get_zeros_sptr ofdm_make_get_zeros(int ll);

/*!

 */
class OFDM_API ofdm_get_zeros : public gr_sync_block
{
  private:
    friend OFDM_API ofdm_get_zeros_sptr ofdm_make_get_zeros(int ll);

    ofdm_get_zeros(int ll);

    int  d_ll;
 
  public:
    virtual ~ofdm_get_zeros() {};

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_GET_ZEROS_H_ */
