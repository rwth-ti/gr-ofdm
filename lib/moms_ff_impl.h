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

#ifndef INCLUDED_OFDM_MOMS_FF_IMPL_H
#define INCLUDED_OFDM_MOMS_FF_IMPL_H

#include <ofdm/moms_ff.h>

namespace gr {
  namespace ofdm {

    class moms_ff_impl : public moms_ff
    {
     private:
      // Interpolation Fraction
	  double                         d_ip_num;
	  double                         d_ip_denom;
	  // Current offset
	  double                         d_offset_num;

     public:
      moms_ff_impl();
      ~moms_ff_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);

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

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_MOMS_FF_IMPL_H */

