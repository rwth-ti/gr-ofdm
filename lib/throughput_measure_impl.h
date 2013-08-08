/* -*- c++ -*- */
/* 
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
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

#ifndef INCLUDED_OFDM_THROUGHPUT_MEASURE_IMPL_H
#define INCLUDED_OFDM_THROUGHPUT_MEASURE_IMPL_H

#include <ofdm/throughput_measure.h>

#ifdef HAVE_SYS_TIME_H
#include <sys/time.h>
#endif

namespace gr {
  namespace ofdm {

    class throughput_measure_impl : public throughput_measure
    {
     private:
        int       d_itemsize;
        double    d_total_samples;
        bool      d_init;
    #ifdef HAVE_SYS_TIME_H
        struct timeval  d_start;
    #endif

        double d_min, d_max, d_avg;

     public:
      throughput_measure_impl(int itemsize);
      ~throughput_measure_impl();

      double get_max() const  { return d_max; }
      double get_min() const  { return d_min; }
      double get_avg() const  { return d_avg; }

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_THROUGHPUT_MEASURE_IMPL_H */

