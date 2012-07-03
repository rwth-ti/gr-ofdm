
/* $Id: ofdm_interp_cir_set_noncir_to_zero.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_INTERP_CIR_SET_NONCIR_TO_ZERO_H_
#define INCLUDED_OFDM_INTERP_CIR_SET_NONCIR_TO_ZERO_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

class ofdm_interp_cir_set_noncir_to_zero;
typedef boost::shared_ptr<ofdm_interp_cir_set_noncir_to_zero> 
  ofdm_interp_cir_set_noncir_to_zero_sptr;
  
OFDM_API ofdm_interp_cir_set_noncir_to_zero_sptr 
ofdm_make_interp_cir_set_noncir_to_zero( int vlen, int window );

/*!

 */
class OFDM_API ofdm_interp_cir_set_noncir_to_zero : public gr_sync_block
{
private:

  ofdm_interp_cir_set_noncir_to_zero( int vlen, int window );

  int  d_vlen;
  int  d_window;
 
public:

  static ofdm_interp_cir_set_noncir_to_zero_sptr
  create( int vlen, int window );

  virtual ~ofdm_interp_cir_set_noncir_to_zero() {};

  int 
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_INTERP_CIR_SET_NONCIR_TO_ZERO_H_ */
