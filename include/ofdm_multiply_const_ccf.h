
/* $Id$ */

#ifndef INCLUDED_OFDM_MULTIPLY_CONST_CCF_H_
#define INCLUDED_OFDM_MULTIPLY_CONST_CCF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

class ofdm_multiply_const_ccf;
typedef boost::shared_ptr<ofdm_multiply_const_ccf>
  ofdm_multiply_const_ccf_sptr;

OFDM_API ofdm_multiply_const_ccf_sptr
ofdm_make_multiply_const_ccf( float k );

/*!

 */
class OFDM_API ofdm_multiply_const_ccf : public gr_sync_block
{
private:

  ofdm_multiply_const_ccf( float k );

  float  d_k;

  typedef unsigned int size_type;

  static size_type const cache_line = 128;
  static size_type const cache_size = cache_line / sizeof( float ); // 32

  float * d_cache;

public:

  void set_k( float k );

  static ofdm_multiply_const_ccf_sptr
  create( float k );

  virtual ~ofdm_multiply_const_ccf();

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_MULTIPLY_CONST_CCF_H_ */
