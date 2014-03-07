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

#ifndef INCLUDED_OFDM_BIT_POSITION_DEPENDENT_BER_IMPL_H
#define INCLUDED_OFDM_BIT_POSITION_DEPENDENT_BER_IMPL_H

#include <ofdm/bit_position_dependent_ber.h>

#include <boost/shared_array.hpp>
#include <string>


namespace gr {
  namespace ofdm {

    class bit_position_dependent_ber_impl : public bit_position_dependent_ber
    {
     private:
    	  std::string   d_filename_prefix;
    	  typedef unsigned int cntr_t;
		  typedef boost::shared_array< cntr_t > cntr_vec_t;

		  typedef unsigned int index_t;

		  index_t               d_index;
		  index_t               d_cntr_len;
		  cntr_vec_t            d_cntr;


		  index_t               d_file_idx;

		  bool                  d_min_reached;

		  void flush();

     public:
      bit_position_dependent_ber_impl(std::string filename_prefix);
      ~bit_position_dependent_ber_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      bool stop();
      std::vector< int > get_cntr_vec() const;

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_BIT_POSITION_DEPENDENT_BER_IMPL_H */

