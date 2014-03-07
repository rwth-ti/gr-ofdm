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

#ifndef INCLUDED_OFDM_VECTOR_SAMPLER_IMPL_H
#define INCLUDED_OFDM_VECTOR_SAMPLER_IMPL_H

#include <ofdm/vector_sampler.h>

/*!
* \brief Sample vector on trigger
*
* inputs:
* - data stream, size=itemsize
* - trigger stream, byte stream
*
* output:
* - sampled vectors, vector stream, size=vlen*itemsize
*
* Function:
* On trigger, it takes the last vlen items, groups them into a vector and
* places the vector in the output stream.
*/

namespace gr {
  namespace ofdm {

    class vector_sampler_impl : public vector_sampler
    {
     private:
    	  int d_itemsize;
    	  int d_vlen;

     public:
      vector_sampler_impl(int itemsize,int vlen);
      ~vector_sampler_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);

      virtual int noutput_forecast( gr_vector_int &ninput_items,
          int available_space, int max_items_avail,
          std::vector<bool> &input_done );
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_VECTOR_SAMPLER_IMPL_H */

