
/* $Id: ofdm_CTF_MSE_enhancer.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_CTF_MSE_ENHANCER_H_
#define INCLUDED_OFDM_CTF_MSE_ENHANCER_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <gr_sync_block.h>

class ofdm_CTF_MSE_enhancer;
typedef boost::shared_ptr<ofdm_CTF_MSE_enhancer>
  ofdm_CTF_MSE_enhancer_sptr;

OFDM_API ofdm_CTF_MSE_enhancer_sptr
ofdm_make_CTF_MSE_enhancer( int vlen, int cir_len );

class gri_fft_complex;
class gri_fft_real_fwd;
class gri_fft_real_rev;

/*! Enhance MSE of CTF estimate
 *
 * Input: CTF estimate
 * Output: MSE enhanced estimate
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
 * Samples outside the window are set to zero. They probable only contain noise.
 * The extracted CIR is re-transformed into CTF. That is our output.
 *
 * vlen must be a multiple of 4.
 */
class OFDM_API ofdm_CTF_MSE_enhancer : public gr_sync_block
{
private:

  ofdm_CTF_MSE_enhancer( int vlen, int cir_len );

  int  d_vlen;
  int  d_cir_len;

  boost::shared_ptr< gri_fft_complex > d_invfft;
  boost::shared_ptr< gri_fft_complex > d_fwdfft;
  boost::shared_ptr< gri_fft_real_rev > d_invrfft;
  boost::shared_ptr< gri_fft_real_fwd > d_fwdrfft;

  gr_complex * buf1; // IFFT in, FFT out
  gr_complex * buf2; // IFFT out, FFT in

  float * buf3;         // real FFT in, real IFFT out
  gr_complex * buf4;    // real FFT out, real IFFT in

  gr_complex * d_fd_filter;

  void
  set_fd_filter();

public:

  static ofdm_CTF_MSE_enhancer_sptr
  create( int vlen, int cir_len );

  virtual ~ofdm_CTF_MSE_enhancer();

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_CTF_MSE_ENHANCER_H_ */
