
/* $Id: ofdm_compat_read_ber_from_imgxfer.h 829 2009-02-25 12:30:54Z auras $ */

#ifndef INCLUDED_OFDM_COMPAT_READ_BER_FROM_IMGXFER_H_
#define INCLUDED_OFDM_COMPAT_READ_BER_FROM_IMGXFER_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_block.h>

class ofdm_compat_read_ber_from_imgxfer;
typedef boost::shared_ptr<ofdm_compat_read_ber_from_imgxfer>
  ofdm_compat_read_ber_from_imgxfer_sptr;

class ofdm_imgtransfer_sink;
typedef boost::shared_ptr<ofdm_imgtransfer_sink>
  ofdm_imgtransfer_sink_sptr;



OFDM_API ofdm_compat_read_ber_from_imgxfer_sptr
ofdm_make_compat_read_ber_from_imgxfer( ofdm_imgtransfer_sink_sptr xfersink );



/*!

 */
class OFDM_API ofdm_compat_read_ber_from_imgxfer : public gr_block
{
private:

  ofdm_compat_read_ber_from_imgxfer( ofdm_imgtransfer_sink_sptr xfersink );

  ofdm_imgtransfer_sink_sptr   d_xfersink;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

public:

  static ofdm_compat_read_ber_from_imgxfer_sptr
  create( ofdm_imgtransfer_sink_sptr xfersink );

  virtual ~ofdm_compat_read_ber_from_imgxfer() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_COMPAT_READ_BER_FROM_IMGXFER_H_ */
