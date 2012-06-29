
/* $Id: ofdm_extract_block_from_frame.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_EXTRACT_BLOCK_FROM_FRAME_H_
#define INCLUDED_OFDM_EXTRACT_BLOCK_FROM_FRAME_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_block.h>

class ofdm_extract_block_from_frame;
typedef boost::shared_ptr<ofdm_extract_block_from_frame>
  ofdm_extract_block_from_frame_sptr;

OFDM_API ofdm_extract_block_from_frame_sptr
ofdm_make_extract_block_from_frame( int vlen, int block_no );

/*!

 */
class OFDM_API ofdm_extract_block_from_frame : public gr_block
{
private:

  ofdm_extract_block_from_frame( int vlen, int block_no );

  int  d_vlen;
  int  d_block_no;
  int  d_ctr;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

public:

  static ofdm_extract_block_from_frame_sptr
  create( int vlen, int block_no );

  virtual ~ofdm_extract_block_from_frame() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_EXTRACT_BLOCK_FROM_FRAME_H_ */
