#ifndef INCLUDED_OFDM_CHANNEL_EQUALIZER_MIMO_H_
#define INCLUDED_OFDM_CHANNEL_EQUALIZER_MIMO_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_block.h>

class ofdm_channel_equalizer_mimo;
typedef boost::shared_ptr<ofdm_channel_equalizer_mimo>
  ofdm_channel_equalizer_mimo_sptr;

OFDM_API ofdm_channel_equalizer_mimo_sptr
ofdm_make_channel_equalizer_mimo( int vlen);

/*!

 */
class OFDM_API ofdm_channel_equalizer_mimo : public gr_block
{
private:

  ofdm_channel_equalizer_mimo( int vlen );

  int  d_vlen;
  int  d_need_input_h0;
  int  d_need_input_h1;


  gr_complex * d_buffer_h0;
  gr_complex * d_buffer_h1;


  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

public:

  static ofdm_channel_equalizer_mimo_sptr
  create( int vlen );

  virtual ~ofdm_channel_equalizer_mimo();

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_CHANNEL_EQUALIZER_MIMO_H_ */
