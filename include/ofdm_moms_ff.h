
/* $Id: ofdm_moms_ff.h 1077 2009-07-07 09:56:33Z rohlfing $ */

#ifndef INCLUDED_OFDM_MOMS_FF_H_
#define INCLUDED_OFDM_MOMS_FF_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_block.h>


class ofdm_moms_ff;
typedef boost::shared_ptr<ofdm_moms_ff>
  ofdm_moms_ff_sptr;

OFDM_API ofdm_moms_ff_sptr
ofdm_make_moms_ff(  );

/*!

 */
class OFDM_API ofdm_moms_ff : public gr_block
{
private:

  ofdm_moms_ff(  );


  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

  // Interpolation Fraction
  double                         d_ip_num;
  double                         d_ip_denom;

  // Current offset
  double                         d_offset_num;


public:

  static ofdm_moms_ff_sptr
  create(  );

  virtual ~ofdm_moms_ff() {};

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

#endif /* INCLUDED_OFDM_MOMS_FF_H_ */
