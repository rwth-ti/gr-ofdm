
/* $Id: ofdm_LS_estimator_straight_slope.h 1110 2009-08-27 20:41:54Z auras $ */

#ifndef INCLUDED_OFDM_LS_ESTIMATOR_STRAIGHT_SLOPE_H_
#define INCLUDED_OFDM_LS_ESTIMATOR_STRAIGHT_SLOPE_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

class ofdm_LS_estimator_straight_slope;
typedef boost::shared_ptr<ofdm_LS_estimator_straight_slope>
  ofdm_LS_estimator_straight_slope_sptr;

OFDM_API ofdm_LS_estimator_straight_slope_sptr
ofdm_make_LS_estimator_straight_slope( int vlen );

/*!

 */
class OFDM_API ofdm_LS_estimator_straight_slope : public gr_sync_block
{
private:

  ofdm_LS_estimator_straight_slope( int vlen );

  int  d_vlen;

  std::vector< float > d_slope_coeff;
  std::vector< float > d_offset_coeff;

public:

  static ofdm_LS_estimator_straight_slope_sptr
  create( int vlen );

  virtual ~ofdm_LS_estimator_straight_slope() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_LS_ESTIMATOR_STRAIGHT_SLOPE_H_ */
