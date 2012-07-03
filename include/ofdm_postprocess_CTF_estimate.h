
/* $Id: ofdm_postprocess_CTF_estimate.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_POSTPROCESS_CTF_ESTIMATE_H_
#define INCLUDED_OFDM_POSTPROCESS_CTF_ESTIMATE_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_sync_block.h>

class ofdm_postprocess_CTF_estimate;
typedef boost::shared_ptr<ofdm_postprocess_CTF_estimate> 
  ofdm_postprocess_CTF_estimate_sptr;
  
OFDM_API ofdm_postprocess_CTF_estimate_sptr 
ofdm_make_postprocess_CTF_estimate( int vlen );

/*!

 */
class OFDM_API ofdm_postprocess_CTF_estimate : public gr_sync_block
{
private:

  ofdm_postprocess_CTF_estimate( int vlen );

  int  d_vlen;
 
public:

  static ofdm_postprocess_CTF_estimate_sptr
  create( int vlen );

  virtual ~ofdm_postprocess_CTF_estimate() {};

  int 
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_POSTPROCESS_CTF_ESTIMATE_H_ */
