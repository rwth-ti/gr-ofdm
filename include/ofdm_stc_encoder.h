#ifndef INCLUDED_OFDM_STC_ENCODER_H_
#define INCLUDED_OFDM_STC_ENCODER_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations

class ofdm_stc_encoder;
typedef boost::shared_ptr<ofdm_stc_encoder>
  ofdm_stc_encoder_sptr;

OFDM_API ofdm_stc_encoder_sptr
ofdm_make_stc_encoder( int vlen, int num_symbols, std::vector< int> const & pilot_subcarriers );

class OFDM_API ofdm_stc_encoder : public gr_sync_block
{
private:

  ofdm_stc_encoder( int vlen, int num_symbols, std::vector< int > const & pilot_subcarriers );

  int  d_vlen;
  int  d_num_symbols;
  std::vector< int >  d_pilot_tone;
  int d_pcount;

//  void
//  init_stc_encoder(
//        const std::vector<int> &pilot_subcarriers);

public:

  static ofdm_stc_encoder_sptr
  create( int vlen, int num_symbols, std::vector< int > const & pilot_subcarriers );

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_STC_ENCODER_H_ */

