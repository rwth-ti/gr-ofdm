
/* $Id: ofdm_sinr_interpolator.h 611 2008-10-20 15:26:52Z auras $ */

#ifndef INCLUDED_OFDM_NOISE_NULLING_H_
#define INCLUDED_OFDM_NOISE_NULLING_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

/*!
  Implementation of Milan's SNR estimation, taking the 1st preamble as input and giving SNR estimate at 1st output and noise estimate at 2nd output
 */

class ofdm_noise_nulling;
typedef boost::shared_ptr<ofdm_noise_nulling>
ofdm_noise_nulling_sptr;

OFDM_API ofdm_noise_nulling_sptr
ofdm_make_noise_nulling( int vlen, int keep);

/*!

 */
class OFDM_API ofdm_noise_nulling : public gr_sync_block
{
private:

	ofdm_noise_nulling( int vlen,
    int keep);

  int   d_vlen;
  int	d_keep;

public:

  static ofdm_noise_nulling_sptr
  create( int vlen, int keep);

  virtual ~ofdm_noise_nulling() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_SINR_INTERPOLATOR_H_ */
