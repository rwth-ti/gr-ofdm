
/* $Id: ofdm_channel_equalizer.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_CHANNEL_EQUALIZER_H_
#define INCLUDED_OFDM_CHANNEL_EQUALIZER_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_block.h>

class ofdm_channel_equalizer;
typedef boost::shared_ptr<ofdm_channel_equalizer>
  ofdm_channel_equalizer_sptr;

OFDM_API ofdm_channel_equalizer_sptr
ofdm_make_channel_equalizer( int vlen );

/*!

 */
class OFDM_API ofdm_channel_equalizer : public gr_block
{
private:

  ofdm_channel_equalizer( int vlen );

  int  d_vlen;
  int d_need_input;

  gr_complex * d_buffer;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

public:

  static ofdm_channel_equalizer_sptr
  create( int vlen );

  virtual ~ofdm_channel_equalizer();

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_CHANNEL_EQUALIZER_H_ */
