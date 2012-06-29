
/* $Id: ofdm_constellation_sample_filter.h 611 2008-10-20 15:26:52Z auras $ */

#ifndef INCLUDED_OFDM_CONSTELLATION_SAMPLE_FILTER_H_
#define INCLUDED_OFDM_CONSTELLATION_SAMPLE_FILTER_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
#include <gr_block.h>

#include <boost/shared_array.hpp>

class ofdm_constellation_sample_filter;
typedef boost::shared_ptr<ofdm_constellation_sample_filter> 
  ofdm_constellation_sample_filter_sptr;
  
OFDM_API ofdm_constellation_sample_filter_sptr 
ofdm_make_constellation_sample_filter( int arity, int vlen );

/*!

 */
class OFDM_API ofdm_constellation_sample_filter : public gr_block
{
private:

  ofdm_constellation_sample_filter( int arity, int vlen );

  int  d_arity;
  int  d_vlen;
  int  d_need_bitmap;
  
  boost::shared_array< char > d_bitmap;
  
  
 
  void 
  forecast( int noutput_items, 
    gr_vector_int &ninput_items_required );

public:

  static ofdm_constellation_sample_filter_sptr
  create( int arity, int vlen );

  virtual ~ofdm_constellation_sample_filter() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_CONSTELLATION_SAMPLE_FILTER_H_ */
