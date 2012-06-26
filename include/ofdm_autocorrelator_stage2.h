
/* $Id: ofdm_autocorrelator_stage2.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_AUTOCORRELATOR_STAGE2_H_
#define INCLUDED_OFDM_AUTOCORRELATOR_STAGE2_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_block.h>

class ofdm_autocorrelator_stage2;
typedef boost::shared_ptr<ofdm_autocorrelator_stage2>
  ofdm_autocorrelator_stage2_sptr;

OFDM_API ofdm_autocorrelator_stage2_sptr
ofdm_make_autocorrelator_stage2( int n_samples );

/*!

 */
class OFDM_API ofdm_autocorrelator_stage2 : public gr_sync_block
{
private:

  ofdm_autocorrelator_stage2( int n_samples );

  int  d_n_samples;
  int  d_delay;

  gr_complex d_acc1;
  float      d_acc2;

public:

  static ofdm_autocorrelator_stage2_sptr
  create( int n_samples );

  virtual ~ofdm_autocorrelator_stage2() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_AUTOCORRELATOR_STAGE2_H_ */
