#ifndef INCLUDED_OFDM_STC_DECODER_RX1_H_
#define INCLUDED_OFDM_STC_DECODER_RX1_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations

class ofdm_stc_decoder_rx1;
typedef boost::shared_ptr<ofdm_stc_decoder_rx1>
  ofdm_stc_decoder_rx1_sptr;

OFDM_API ofdm_stc_decoder_rx1_sptr
ofdm_make_stc_decoder_rx1( int vlen );

class OFDM_API ofdm_stc_decoder_rx1 : public gr_sync_block
{
private:

  ofdm_stc_decoder_rx1( int vlen );

  int  d_vlen;

public:

  static ofdm_stc_decoder_rx1_sptr
  create( int vlen );

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_STC_DECODER_RX1_H_ */

