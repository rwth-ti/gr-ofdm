
/* $Id: ofdm_sinr_interpolator.h 611 2008-10-20 15:26:52Z auras $ */

#ifndef INCLUDED_OFDM_SNR_ESTIMATOR_H_
#define INCLUDED_OFDM_SNR_ESTIMATOR_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

/*!
  Implementation of Milan's SNR estimation, taking the 1st preamble as input and giving SNR estimate at 1st output and noise estimate at 2nd output
 */

class ofdm_snr_estimator;
typedef boost::shared_ptr<ofdm_snr_estimator>
ofdm_snr_estimator_sptr;

OFDM_API ofdm_snr_estimator_sptr
ofdm_make_snr_estimator( int vlen, int skip);

/*!

 */
class OFDM_API ofdm_snr_estimator : public gr_sync_block
{
private:

	ofdm_snr_estimator( int vlen,
    int skip);

  int   d_vlen;
  int	d_skip;

public:

  static ofdm_snr_estimator_sptr
  create( int vlen, int skip);

  virtual ~ofdm_snr_estimator() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_SINR_INTERPOLATOR_H_ */
