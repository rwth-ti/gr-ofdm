
/* $Id$ */

#ifndef INCLUDED_OFDM_MEAN_SQUARED_ERROR_H_
#define INCLUDED_OFDM_MEAN_SQUARED_ERROR_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>// forward declarations
#include <gr_block.h>

class ofdm_mean_squared_error;
typedef boost::shared_ptr<ofdm_mean_squared_error>
  ofdm_mean_squared_error_sptr;

OFDM_API ofdm_mean_squared_error_sptr
ofdm_make_mean_squared_error( int vlen, unsigned long window, bool reset,
  double norm_factor );

/*!

 */
class OFDM_API ofdm_mean_squared_error : public gr_block
{
private:

  ofdm_mean_squared_error( int vlen, unsigned long window, bool reset,
    double norm_factor );

  int  		 d_vlen;
  unsigned long  d_window;
  bool  	 d_reset;
  double  	 d_norm_factor;
  unsigned long  d_cnt;
  double	 d_acc;

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

public:

  static ofdm_mean_squared_error_sptr
  create( int vlen, unsigned long window, bool reset, double norm_factor );

  virtual ~ofdm_mean_squared_error() {};

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

  void reset() { d_acc = 0.0; d_cnt = d_window; }

};

#endif /* INCLUDED_OFDM_MEAN_SQUARED_ERROR_H_ */
