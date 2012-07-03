
/* $Id: ofdm_reassemble_ofdm_frame.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_REASSEMBLE_OFDM_FRAME_H_
#define INCLUDED_OFDM_REASSEMBLE_OFDM_FRAME_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_block.h>

class ofdm_reassemble_ofdm_frame;
typedef boost::shared_ptr<ofdm_reassemble_ofdm_frame>
  ofdm_reassemble_ofdm_frame_sptr;

OFDM_API ofdm_reassemble_ofdm_frame_sptr
ofdm_make_reassemble_ofdm_frame( int vlen, int framelength );

/*!

 */
class OFDM_API ofdm_reassemble_ofdm_frame : public gr_block
{
private:

  ofdm_reassemble_ofdm_frame( int vlen, int framelength );

  int  d_vlen;
  int  d_framelength;

  int d_blk;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

public:

  static ofdm_reassemble_ofdm_frame_sptr
  create( int vlen, int framelength );

  virtual ~ofdm_reassemble_ofdm_frame() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_REASSEMBLE_OFDM_FRAME_H_ */
