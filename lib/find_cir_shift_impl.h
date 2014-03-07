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

#ifndef INCLUDED_OFDM_FIND_CIR_SHIFT_IMPL_H
#define INCLUDED_OFDM_FIND_CIR_SHIFT_IMPL_H

#include <ofdm/find_cir_shift.h>

#include <gnuradio/fft/fft.h>
#include <vector>


namespace gr {
  namespace ofdm {

    class find_cir_shift_impl : public find_cir_shift
    {
     private:
    	  int  d_vlen;
    	  int  d_cir_len;


    	  boost::shared_ptr< gr::fft::fft_complex  > d_invfft;
    	  boost::shared_ptr< gr::fft::fft_real_fwd > d_fwdrfft;
    	  boost::shared_ptr< gr::fft::fft_real_rev > d_invrfft;

    	  gr_complex * buf1; // IFFT in,
    	  gr_complex * buf2; // IFFT out

    	  float * buf3;         // real FFT in, real IFFT out
    	  gr_complex * buf4;    // real FFT out, real IFFT in

    	  gr_complex * d_fd_filter;

    	  void
    	  set_fd_filter();

     public:
      find_cir_shift_impl(int vlen, int cir_len);
      ~find_cir_shift_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_FIND_CIR_SHIFT_IMPL_H */

