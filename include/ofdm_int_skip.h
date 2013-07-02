
/* $Id: ofdm_int_skip.h 611 2008-10-20 15:26:52Z auras $ */

#ifndef INCLUDED_OFDM_INT_SKIP_H_
#define INCLUDED_OFDM_INT_SKIP_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations

/*!
  Taking each skip element of the vector imput
 */

class ofdm_int_skip;
typedef boost::shared_ptr<ofdm_int_skip>
ofdm_int_skip_sptr;

OFDM_API ofdm_int_skip_sptr
ofdm_make_int_skip( int vlen, int skip, int start);

/*!

 */
class OFDM_API ofdm_int_skip : public gr_sync_block
{
private:

	ofdm_int_skip( int vlen,
    int skip, int start);

  int   d_vlen;
  int	d_skip;
  int	d_start;

public:

  static ofdm_int_skip_sptr
  create( int vlen, int skip, int start);

  virtual ~ofdm_int_skip() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_SINR_INTERPOLATOR_H_ */
