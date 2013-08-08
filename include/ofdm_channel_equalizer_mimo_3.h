#ifndef INCLUDED_OFDM_channel_equalizer_mimo_3_H_
#define INCLUDED_OFDM_channel_equalizer_mimo_3_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations

class ofdm_channel_equalizer_mimo_3;
typedef boost::shared_ptr<ofdm_channel_equalizer_mimo_3>
  ofdm_channel_equalizer_mimo_3_sptr;

OFDM_API ofdm_channel_equalizer_mimo_3_sptr
ofdm_make_channel_equalizer_mimo_3( int vlen);

/*!

 */
class OFDM_API ofdm_channel_equalizer_mimo_3 : public gr_block
{
private:

  ofdm_channel_equalizer_mimo_3( int vlen );

  int  d_vlen;
  int  d_need_input_h0;
  int  d_need_input_h1;
  int  d_need_input_h2;
  int  d_need_input_h3;

  gr_complex * d_buffer_h0;
  gr_complex * d_buffer_h1;
  gr_complex * d_buffer_h2;
  gr_complex * d_buffer_h3;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

public:

  static ofdm_channel_equalizer_mimo_3_sptr
  create( int vlen );

  virtual ~ofdm_channel_equalizer_mimo_3();

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_channel_equalizer_mimo_3_H_ */
