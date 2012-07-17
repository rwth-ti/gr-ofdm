
/* $Id: ofdm_find_cir_shift.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_FIND_CIR_SHIFT_H_
#define INCLUDED_OFDM_FIND_CIR_SHIFT_H_

#include <ofdm_api.h>
#include <gr_sync_block.h>
#include <vector>

class ofdm_find_cir_shift;
typedef boost::shared_ptr<ofdm_find_cir_shift>
  ofdm_find_cir_shift_sptr;

OFDM_API ofdm_find_cir_shift_sptr
ofdm_make_find_cir_shift( int vlen, int cir_len );

class gri_fft_complex;
class gri_fft_real_fwd;
class gri_fft_real_rev;

/*! Find CIR shift
 *
 * Input: CTF estimate
 *
 * The first tap of the CIR may not be at the beginning of the window. We
 * try to estimate the position of this first tap.
 *
 * First, we compute the CIR from the CTF input via IFFT. We use a rect-window
 * of size cir_len that we position within the block. The position where the
 * energy within the window reaches its maximum is our estimate for the
 * position of the first tap.
 *
 * Note: If the current CIR length is smaller than cir_len (the window size)
 * there are multiple optimal window positions and hence we encounter
 * ambiguities.
 *
 * vlen must be a multiple of 4.
 */

class OFDM_API ofdm_find_cir_shift : public gr_sync_block
{
private:

  ofdm_find_cir_shift( int vlen, int cir_len );

  int  d_vlen;
  int  d_cir_len;


  boost::shared_ptr< gri_fft_complex > d_invfft;
  boost::shared_ptr< gri_fft_real_rev > d_invrfft;
  boost::shared_ptr< gri_fft_real_fwd > d_fwdrfft;

  gr_complex * buf1; // IFFT in,
  gr_complex * buf2; // IFFT out

  float * buf3;         // real FFT in, real IFFT out
  gr_complex * buf4;    // real FFT out, real IFFT in

  gr_complex * d_fd_filter;

  void
  set_fd_filter();

public:

  static ofdm_find_cir_shift_sptr
  create( int vlen, int cir_len );

  virtual ~ofdm_find_cir_shift();

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_FIND_CIR_SHIFT_H_ */
