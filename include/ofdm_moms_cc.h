
/* $Id$ */

#ifndef INCLUDED_OFDM_MOMS_CC_H_
#define INCLUDED_OFDM_MOMS_CC_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_block.h>

class ofdm_moms_cc;
typedef boost::shared_ptr<ofdm_moms_cc> 
  ofdm_moms_cc_sptr;
  
OFDM_API ofdm_moms_cc_sptr 
ofdm_make_moms_cc( double ip_num, double ip_denom );

/*!

 */
class OFDM_API ofdm_moms_cc : public gr_block
{
private:

  ofdm_moms_cc( double ip_num, double ip_denom );

  double  d_ip_num;
  double  d_ip_denom;
  double  d_offset_num;
 
  void 
  forecast( int noutput_items, 
    gr_vector_int &ninput_items_required );

public:

  static ofdm_moms_cc_sptr
  create( double ip_num, double ip_denom );

  virtual ~ofdm_moms_cc() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

  // GET / SET
  void
  set_init_ip_fraction(double num, double denom);
  void
  set_ip_fraction(double num, double denom);
  double
  get_ip_fraction_num();
  double
  get_ip_fraction_denom();

  void
  set_offset_num(double num);
  double
  get_offset_num();

};

#endif /* INCLUDED_OFDM_MOMS_CC_H_ */
