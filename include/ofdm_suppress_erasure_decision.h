
/* $Id$ */

#ifndef INCLUDED_OFDM_SUPPRESS_ERASURE_DECISION_H_
#define INCLUDED_OFDM_SUPPRESS_ERASURE_DECISION_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_block.h>

class ofdm_suppress_erasure_decision;
typedef boost::shared_ptr<ofdm_suppress_erasure_decision> 
  ofdm_suppress_erasure_decision_sptr;
  
OFDM_API ofdm_suppress_erasure_decision_sptr 
ofdm_make_suppress_erasure_decision(  );

/*!

 */
class OFDM_API ofdm_suppress_erasure_decision : public gr_block
{
private:

  ofdm_suppress_erasure_decision(  );

 
  void 
  forecast( int noutput_items, 
    gr_vector_int &ninput_items_required );

public:

  static ofdm_suppress_erasure_decision_sptr
  create(  );

  virtual ~ofdm_suppress_erasure_decision() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_SUPPRESS_ERASURE_DECISION_H_ */
