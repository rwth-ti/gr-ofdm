
/* $Id: ofdm_autocorrelator.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_AUTOCORRELATOR_H_
#define INCLUDED_OFDM_AUTOCORRELATOR_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_hier_block2.h>

class ofdm_autocorrelator;
typedef boost::shared_ptr<ofdm_autocorrelator>
  ofdm_autocorrelator_sptr;

// OFDM_API is to be added here
OFDM_API ofdm_autocorrelator_sptr
ofdm_make_autocorrelator( int lag, int n_samples );

class ofdm_autocorrelator_stage1;
class ofdm_autocorrelator_stage2;
typedef boost::shared_ptr< ofdm_autocorrelator_stage1 >
  ofdm_autocorrelator_stage1_sptr;
typedef boost::shared_ptr< ofdm_autocorrelator_stage2 >
  ofdm_autocorrelator_stage2_sptr;

/*!

 */
class OFDM_API ofdm_autocorrelator : public gr_hier_block2
{
private:

  ofdm_autocorrelator( int lag, int n_samples );

  int  d_lag;
  int  d_n_samples;

  ofdm_autocorrelator_stage1_sptr d_s1;
  ofdm_autocorrelator_stage2_sptr d_s2;

public:

  static ofdm_autocorrelator_sptr
  create( int lag, int n_samples );

  virtual ~ofdm_autocorrelator() {};

};

#endif /* INCLUDED_OFDM_AUTOCORRELATOR_H_ */
