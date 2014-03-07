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

#ifndef INCLUDED_OFDM_TRIGGER_SURVEILLANCE_IMPL_H
#define INCLUDED_OFDM_TRIGGER_SURVEILLANCE_IMPL_H

#include <ofdm/trigger_surveillance.h>

namespace gr {
  namespace ofdm {

    class trigger_surveillance_impl : public trigger_surveillance
    {
     private:
        long long  d_ideal_distance;
        long long  d_max_shift;
        long long d_dist;
        unsigned long long d_lost;
        bool d_first;


     public:
      trigger_surveillance_impl(int ideal_distance, int max_shift);
      ~trigger_surveillance_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);

      unsigned long long lost_triggers() { return d_lost; };
      void reset_counter() { d_lost = 0; };
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_TRIGGER_SURVEILLANCE_IMPL_H */

