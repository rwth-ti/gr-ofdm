
/* $Id: ofdm_multiply_const_vcc.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_MULTIPLY_CONST_VCC_H_
#define INCLUDED_OFDM_MULTIPLY_CONST_VCC_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

class ofdm_multiply_const_vcc;
typedef boost::shared_ptr<ofdm_multiply_const_vcc>
  ofdm_multiply_const_vcc_sptr;

OFDM_API ofdm_multiply_const_vcc_sptr
ofdm_make_multiply_const_vcc( std::vector< gr_complex > const & k );

/*!

 */
class OFDM_API ofdm_multiply_const_vcc : public gr_sync_block
{
private:

  ofdm_multiply_const_vcc( std::vector< gr_complex > const & k );

  int d_vlen;
  gr_complex * d_buffer;

public:

  static ofdm_multiply_const_vcc_sptr
  create( std::vector< gr_complex > const & k );

  virtual ~ofdm_multiply_const_vcc();

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_MULTIPLY_CONST_VCC_H_ */
