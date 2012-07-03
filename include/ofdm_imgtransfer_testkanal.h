
/* $Id$ */

#ifndef INCLUDED_OFDM_IMGTRANSFER_TESTKANAL_H_
#define INCLUDED_OFDM_IMGTRANSFER_TESTKANAL_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_block.h>

class ofdm_imgtransfer_testkanal;
typedef boost::shared_ptr<ofdm_imgtransfer_testkanal> 
  ofdm_imgtransfer_testkanal_sptr;
  
OFDM_API ofdm_imgtransfer_testkanal_sptr 
ofdm_make_imgtransfer_testkanal(  );

/*!

 */
class OFDM_API ofdm_imgtransfer_testkanal : public gr_block
{
private:

  ofdm_imgtransfer_testkanal(  );

  unsigned int d_bitcount; 
  int d_pos, d_produced;
  
  int d_flag;
  
  unsigned int d_frameno;
 
  void 
  forecast( int noutput_items, 
    gr_vector_int &ninput_items_required );

public:

  static ofdm_imgtransfer_testkanal_sptr
  create(  );

  virtual ~ofdm_imgtransfer_testkanal() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_IMGTRANSFER_TESTKANAL_H_ */
