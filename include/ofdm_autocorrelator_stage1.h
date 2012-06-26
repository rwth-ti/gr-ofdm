
/* $Id: ofdm_autocorrelator_stage1.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_AUTOCORRELATOR_STAGE1_H_
#define INCLUDED_OFDM_AUTOCORRELATOR_STAGE1_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_block.h>

class ofdm_autocorrelator_stage1;
typedef boost::shared_ptr<ofdm_autocorrelator_stage1>
  ofdm_autocorrelator_stage1_sptr;

OFDM_API ofdm_autocorrelator_stage1_sptr
ofdm_make_autocorrelator_stage1( int lag );

/*!

 */
class OFDM_API ofdm_autocorrelator_stage1 : public gr_sync_block
{
private:

  ofdm_autocorrelator_stage1( int lag );

  int  d_lag;
  int  d_delay;

public:

  static ofdm_autocorrelator_stage1_sptr
  create( int lag );

  virtual ~ofdm_autocorrelator_stage1() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_AUTOCORRELATOR_STAGE1_H_ */
