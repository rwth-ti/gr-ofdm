/* -*- c++ -*- */
/* 
 * Copyright 2014 Institute for Theoretical Information Technology,
 *                RWTH Aachen University
 *                www.ti.rwth-aachen.de
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_OFDM_CTF_MSE_ENHANCER_IMPL_H
#define INCLUDED_OFDM_CTF_MSE_ENHANCER_IMPL_H

#include <ofdm/CTF_MSE_enhancer.h>



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

namespace gr {
  namespace ofdm {

    class CTF_MSE_enhancer_impl : public CTF_MSE_enhancer
    {
     private:
	  int  d_vlen;
	  int  d_cir_len;
//	  class gri_fft_complex;
//	  class gri_fft_real_fwd;
//	  class gri_fft_real_rev;

	  boost::shared_ptr< gr::fft::fft_complex > d_invfft;
	  boost::shared_ptr< gr::fft::fft_complex > d_fwdfft;
	  boost::shared_ptr< gr::fft::fft_real_fwd > d_fwdrfft;
	  boost::shared_ptr< gr::fft::fft_real_rev > d_invrfft;

	  gr_complex * buf1; // IFFT in, FFT out
	  gr_complex * buf2; // IFFT out, FFT in

	  float * buf3;         // real FFT in, real IFFT out
	  gr_complex * buf4;    // real FFT out, real IFFT in

	  gr_complex * d_fd_filter;

	  void
	  set_fd_filter();

     public:
      CTF_MSE_enhancer_impl(int vlen, int cir_len);
      ~CTF_MSE_enhancer_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CTF_MSE_ENHANCER_IMPL_H */

