
/* $Id$ */

#ifndef INCLUDED_OFDM_FRAME_MUX_H_
#define INCLUDED_OFDM_FRAME_MUX_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_block.h>

class ofdm_frame_mux;
typedef boost::shared_ptr<ofdm_frame_mux>
  ofdm_frame_mux_sptr;

OFDM_API ofdm_frame_mux_sptr
ofdm_make_frame_mux( int vlen, int frame_len );

/*!

 */
class OFDM_API ofdm_frame_mux : public gr_block
{
private:

  ofdm_frame_mux( int vlen, int frame_len );

  int  d_vlen;
  int  d_frame_len;
  int  d_preambles;
  int  d_data_blocks;

  typedef float * cache_ptr __attribute__ ((aligned(16)));
  typedef unsigned int size_type;

  cache_ptr d_frame_head;
  size_type d_head_size;
  size_type d_data_size;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

  void update();

public:

  void add_preamble( std::vector< gr_complex > const & );

  static ofdm_frame_mux_sptr
  create( int vlen, int frame_len );

  virtual ~ofdm_frame_mux();

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_FRAME_MUX_H_ */
