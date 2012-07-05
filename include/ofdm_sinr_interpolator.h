
/* $Id: ofdm_sinr_interpolator.h 611 2008-10-20 15:26:52Z auras $ */

#ifndef INCLUDED_OFDM_SINR_INTERPOLATOR_H_
#define INCLUDED_OFDM_SINR_INTERPOLATOR_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

class ofdm_sinr_interpolator;
typedef boost::shared_ptr<ofdm_sinr_interpolator>
ofdm_sinr_interpolator_sptr;

OFDM_API ofdm_sinr_interpolator_sptr
ofdm_make_sinr_interpolator( int vlen, int skip,
   const std::vector<int> &load_index );

/*!

 */
class OFDM_API ofdm_sinr_interpolator : public gr_sync_block
{
private:

	ofdm_sinr_interpolator( int vlen,
    int skip,
    const std::vector<int> &load_index );

  int   d_vlen;
  int	d_skip;
  std::vector<int>   d_load_index;

public:

  static ofdm_sinr_interpolator_sptr
  create( int vlen, int skip,
    const std::vector<int> &load_index );

  virtual ~ofdm_sinr_interpolator() {};

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_SINR_INTERPOLATOR_H_ */
