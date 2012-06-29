
/* $Id: ofdm_coded_bpsk_soft_decoder.h 1045 2009-07-02 13:11:52Z auras $ */

#ifndef INCLUDED_OFDM_CODED_BPSK_SOFT_DECODER_H_
#define INCLUDED_OFDM_CODED_BPSK_SOFT_DECODER_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <vector>
#include <gr_sync_block.h>

class ofdm_coded_bpsk_soft_decoder;
typedef boost::shared_ptr<ofdm_coded_bpsk_soft_decoder>
  ofdm_coded_bpsk_soft_decoder_sptr;

OFDM_API ofdm_coded_bpsk_soft_decoder_sptr
ofdm_make_coded_bpsk_soft_decoder( int vlen, int output_bits,
  const std::vector<int>& whitener,
  std::vector< int > const mask = std::vector< int >() );

/*!

 */
class OFDM_API ofdm_coded_bpsk_soft_decoder : public gr_sync_block
{
private:

  ofdm_coded_bpsk_soft_decoder( int vlen, int output_bits,
    const std::vector<int>& whitener,
    std::vector< int > const & mask );

  int   d_vlen;
  int   d_output_bits;
  std::vector<float>   d_whitener;

  std::vector< bool >  d_mask;

public:

  static ofdm_coded_bpsk_soft_decoder_sptr
  create( int vlen, int output_bits, const std::vector<int>& whitener,
    std::vector< int > const mask );

  virtual ~ofdm_coded_bpsk_soft_decoder() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_CODED_BPSK_SOFT_DECODER_H_ */
